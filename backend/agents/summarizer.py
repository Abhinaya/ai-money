from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
import pandas as pd
from .base import AgentState, get_llm
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class SummaryAgent:
    def __init__(self):
        self.llm = get_llm()

    def create_summary(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        command = state["command"]
        transactions = state["transactions"]

        # Convert transactions to DataFrame for analysis
        df = self._transactions_to_df(transactions)

        summary_data = {}
        plots = []

        if "by category" in command.lower():
            category_summary = self._summarize_by_category(df)
            summary_data["category"] = category_summary
            plots.append(self._create_category_plot(df))

        if "by date" in command.lower():
            date_summary = self._summarize_by_date(df)
            summary_data["date"] = date_summary
            plots.append(self._create_timeline_plot(df))

        state["summary_data"] = summary_data
        state["plots"] = plots

        # Generate natural language summary
        summary_prompt = self._create_summary_prompt(summary_data)
        summary_response = self.llm.invoke([HumanMessage(content=summary_prompt)])

        state["messages"].append(AIMessage(content=summary_response.content))
        return state

    def _transactions_to_df(self, transactions) -> pd.DataFrame:
        # Convert beancount transactions to DataFrame
        data = []
        for txn in transactions:
            data.append({
                'date': txn.date,
                'payee': txn.payee,
                'narration': txn.narration,
                'amount': abs(txn.postings[0].units.number),
                'category': next(p.account for p in txn.postings if p.account.startswith('Expenses:'))
            })
        return pd.DataFrame(data)

    def _create_category_plot(self, df: pd.DataFrame):
        fig = px.pie(df, values='amount', names='category',
                     title='Expenses by Category')
        return fig

    def _create_timeline_plot(self, df: pd.DataFrame):
        fig = px.line(df.groupby('date')['amount'].sum().reset_index(),
                      x='date', y='amount',
                      title='Daily Expenses Over Time')
        return fig
