from beancount.core.data import Transaction
from langchain_core.messages import HumanMessage, SystemMessage
import json
from typing import List


from accounting.catagory import CATEGORIES, BATCH_SIZE
from agents.base import AgentState, TransactionForFeedback, get_llm

class CategorizationAgent:
    def __init__(self):
        self.llm = get_llm()
        self.batch_size = BATCH_SIZE

    async def process_batch(self, state: AgentState) -> AgentState:
        while state.uncategorized_txns:
            batch = state.uncategorized_txns[:self.batch_size]
            await self.categorize_this_batch(batch, state)
            if state.txns_to_get_feedback:
                print("CategorizationAgent.process_batch: To get user feedback ")
                return state
        print("CategorizationAgent.process_batch: Done")
        return state

    async def categorize_this_batch(self, batch, state):
        messages = [
            SystemMessage(content=self._create_system_prompt(state)),
            HumanMessage(content=self._format_transactions_for_prompt(batch))
        ]
        print(f"invoking LLM: {messages}")
        response = str(self.llm.invoke(messages).content)
        print(f"LLM response: {response}")
        try:
            txn_categories = json.loads(response)
            print("categories before: ", txn_categories)
            for txn_id, category_summary in txn_categories.items():
                assessed_category = category_summary["assessed_category"]
                print("assessed_category: ", assessed_category)
                if assessed_category not in CATEGORIES:
                    txn_categories[txn_id] = {"assessed_category": "Expenses:Uncategorized",
                                              "assessed_vendor": category_summary["assessed_vendor"]}
            self._create_categorization_summary(batch, txn_categories, state)
            await state.flush_to_store()
        except json.JSONDecodeError:
            print("JSONDecodeError")
            raise "Error while categorizing."
        return state

    def _create_system_prompt(self, state: AgentState) -> str:
        sample_response = """{
            "20240101-1299-ab3d4f": {"assessed_category": "Expenses:Groceries", "assessed_vendor": "Walmart"},
            "20240101-3499-ec5a2b": {"assessed_category": "Expenses:Restaurant", "assessed_vendor": "Chipotle"}
        }"""
        prompt = f"""You are a financial transaction categorizer.
            Categorize each transaction into one of the following categories and suggest a meaningful subaccount based on the vendor or payee:
            Ensure each catagory is ONLY from {", ".join(CATEGORIES)}.

            Rules:
            - Do NOT suggest any new catagory. Find the closest one and return. If not, return as 'Expenses:Uncategorized'
            - Return the categorization in JSON format with transaction link as key and full account path as value
            - Account path should be in format Category:Subaccount
            - The subaccount should be a clean, normalized version of the vendor name or transaction type or payee name
            - provide valid JSON response only

            Example response format:
                {sample_response}"""
        print("Catagorizer system prompt: ", prompt)
        return prompt

    def _format_transactions_for_prompt(self, transactions: List[Transaction]) -> str:
        formatted = "Transactions to categorize:\n"
        for txn in transactions:
            link = next(iter(txn.links)) if txn.links else "NO_LINK"
            vendor = txn.narration
            payee = txn.payee
            amount = txn.postings[0].units.number
            formatted += f"- Link: {link}, Payee: {payee}, Vendor: {vendor}, Amount: {amount}\n"
        return formatted

    def _create_categorization_summary(self, transactions: List[Transaction], txn_categories: dict, state: AgentState):
        print("txn_categories: ", txn_categories)
        for txn in transactions:
            txn_id = next(iter(txn.links))
            print("txn_id: ", txn_id, txn_categories.get(txn_id, None))
            if txn_categories[txn_id]["assessed_category"] == "Expenses:Uncategorized":
                state.txns_to_get_feedback.append(TransactionForFeedback(
                    transaction=txn,
                    assessed_category=txn_categories[txn_id]["assessed_category"],
                    assessed_vendor=txn_categories[txn_id]["assessed_vendor"],
                ))
            else:
                state.txns_to_update.append({"id": txn_id,
                    "rectified_category":  txn_categories[txn_id]["assessed_category"],
                    "rectified_vendor": txn_categories[txn_id]["assessed_vendor"]})
