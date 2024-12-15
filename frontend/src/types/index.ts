export interface Transaction {
  id: string;
  date: string;
  vendor: string;
  amount: number;
  assessed_category: string;
  assessed_vendor: string;
  rectified_category?: string;
  rectified_vendor?: string;
}

export interface WorkflowState {
  sessionId: string | null;
  totalTransactions: number;
  categories: string[];
  categorizedTransactions: Transaction[];
  isLoading: boolean;
  error: string | null;
}
