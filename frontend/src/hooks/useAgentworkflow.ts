import { useState, useEffect, useCallback } from "react";

type WorkflowState = {
  currentStep: string;
  progress: {
    total: number;
    processed: number;
  };
  summary: any;
};

type Transaction = {
  id: string;
  date: string;
  vendor: string;
  amount: string;
  assessed_category: string;
  assessed_vendor: string;
  rectified_vendor: string;
  rectified_category: string;
};

export function useAgentWorkflow() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [state, setState] = useState<WorkflowState | null>(null);
  const [pendingTransactions, setPendingTransactions] = useState<Transaction[]>(
    [],
  );
  const [categories, setCategories] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initializeConnection = useCallback(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/workflow");

    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case "SESSION_INITIALIZED":
          setState((prev) => ({
            ...prev!,
            currentStep: "Session Initialized",
            progress: message.data.progress,
            session_id: message.data.session_id,
          }));
          break;
        case "STATE_UPDATE":
          setState((prev) => ({
            ...prev!,
            currentStep: message.data.current_step,
            progress: message.data.progress,
            session_id: message.data.session_id,
          }));
          break;

        case "FEEDBACK_REQUIRED":
          console.log(message.data);
          setCategories(message.data.categories);
          setPendingTransactions(message.data.transactions);
          break;

        case "COMPLETE":
          setState((prev) => ({
            ...prev!,
            currentStep: "completed",
            summary: message.data.summary,
          }));
          break;

        case "ERROR":
          setError(message.message);
          break;
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      setSocket(null);
    };

    return () => {
      ws.close();
    };
  }, []);

  const submitFeedback = useCallback(
    (transactions: Array<Transaction>) => {
      if (socket && isConnected) {
        socket.send(
          JSON.stringify({
            type: "SUBMIT_FEEDBACK",
            data: { transactions },
          }),
        );
        setPendingTransactions([]);
      }
    },
    [socket, isConnected],
  );

  const rectifyTransaction = (transaction: Transaction) => {
    if (!pendingTransactions) return;
    setPendingTransactions(
      pendingTransactions.map((t: Transaction) =>
        t.id === transaction.id
          ? {
              ...t,
              rectified_category: transaction.rectified_category,
              rectified_vendor: transaction.rectified_vendor,
            }
          : t,
      ),
    );
  };

  return {
    isConnected,
    currentState: state?.currentStep,
    progress: state?.progress,
    summary: state?.summary,
    categories,
    pendingTransactions,
    error,
    submitFeedback,
    rectifyTransaction,
    initializeConnection,
  };
}
