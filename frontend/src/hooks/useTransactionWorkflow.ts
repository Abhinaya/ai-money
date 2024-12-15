import { useState, useEffect } from "react";
import axios from "axios";
import { WorkflowState, Transaction } from "@/types";

axios.defaults.baseURL = "http://127.0.0.1:8000";

export function useTransactionWorkflow() {
  const [state, setState] = useState<WorkflowState>({
    sessionId: null, // Initially null to match SSR
    totalTransactions: 0,
    categories: [],
    categorizedTransactions: [],
    isLoading: false,
    error: null,
  });

  const [isHydrated, setIsHydrated] = useState(false); // Track hydration status

  useEffect(() => {
    setIsHydrated(true); // Indicate that the component is hydrated
    const sessionId = localStorage.getItem("session_id");
    if (sessionId) {
      setState((prev) => ({ ...prev, sessionId }));
    }
  }, []);

  const initializeTransactions = async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const { data } = await axios.post("/api/init-transactions");
      setState((prev) => ({
        ...prev,
        sessionId: data.session_id,
        totalTransactions: data.total_transactions,
      }));
      if (isHydrated) {
        localStorage.setItem("session_id", data.session_id);
      }
    } catch (error) {
      console.log(error);
      setState((prev) => ({ ...prev, error: "Failed to load transactions" }));
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const startCategorization = async () => {
    if (!state.sessionId) return;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const { data } = await axios.post("/api/categorize", {
        session_id: state.sessionId,
      });
      setState((prev) => ({
        ...prev,
        categories: data.categories,
        categorizedTransactions: data.transactions,
      }));
    } catch (error) {
      console.log(error);
      setState((prev) => ({ ...prev, error: "Categorization failed" }));
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const rectifyCategory = (transaction: Transaction) => {
    setState((prev) => ({
      ...prev,
      categorizedTransactions: prev.categorizedTransactions.map((t) =>
        t.id === transaction.id
          ? {
              ...t,
              rectified_category: transaction.rectified_category,
              rectified_vendor: transaction.rectified_vendor,
            }
          : t,
      ),
    }));
  };

  const submitFeedback = async (updatedTransactions: Transaction[]) => {
    if (!state.sessionId) return;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      await axios.post("/api/submit-feedback", {
        transactions: updatedTransactions.map((t) => ({
          id: t.id,
          date: t.date,
          vendor: t.vendor,
          amount: t.amount,
          assessed_category: t.assessed_category,
          rectified_category: t.rectified_category,
          assessed_vendor: t.assessed_vendor,
          rectified_vendor: t.rectified_vendor,
        })),
        session_id: state.sessionId,
      });
      setState((prev) => ({
        ...prev,
        categories: [],
        categorizedTransactions: [],
        totalTransactions: 0,
        sessionId: null, // Reset session ID
      }));
      if (isHydrated) {
        localStorage.removeItem("session_id");
      }
    } catch (error) {
      console.log(error);
      setState((prev) => ({ ...prev, error: "Failed to submit feedback" }));
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  return {
    ...state,
    isHydrated, // Expose hydration status if needed
    initializeTransactions,
    startCategorization,
    submitFeedback,
    rectifyCategory: rectifyCategory,
  };
}
