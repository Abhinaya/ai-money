"use client";

import { useAgentWorkflow } from "@/hooks/useAgentworkflow";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export function TransactionFlowClient() {
  const [isMounted, setIsMounted] = useState(false);
  const {
    isConnected,
    currentState,
    progress,
    categories,
    pendingTransactions,
    error,
    submitFeedback,
    rectifyTransaction,
    initializeConnection,
  } = useAgentWorkflow();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Don't render anything until the component is mounted
  if (!isMounted) {
    return null;
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold pb-10">Categorize my transactions</h1>

      {!isConnected && currentState !== "completed" && (
        <button
          onClick={initializeConnection}
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Start Processing
        </button>
      )}

      {currentState && currentState === "completed" && (
        <div className="place-items-center">
          <h3 className="text-2xl text-green-700 font-extrabold">
            Categorization is complete 🎉
          </h3>
        </div>
      )}

      {progress && (
        <div className="pt-5">
          <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
            <div
              className="bg-green-400 h-4 rounded-full transition-all duration-500"
              style={{
                width: `${(progress.processed / progress.total) * 100}%`,
              }}
            ></div>
          </div>{" "}
          <div className="text-sky-600 font-bold pt-5">
            All transactions: {progress.total} | Categorized transactions:{" "}
            {progress.processed}
          </div>
        </div>
      )}
      <div className="text-xs font-mono float-right">
        Connection Status: {isConnected ? "Connected" : "Disconnected"}
      </div>
      {isConnected && (
        <div className="space-y-4">
          {error && <div className="text-red-500">Error: {error}</div>}
          {pendingTransactions.length > 0 && (
            <div className="bg-white pb-5 rounded-lg shadow">
              <h2 className="text-lg font-semibold pt-5 mb-4">
                Review and update transaction categories
              </h2>
              <hr />
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="font-bold">Date</TableHead>
                      <TableHead className="font-bold">Expense</TableHead>
                      <TableHead className="font-bold">Amount</TableHead>
                      <TableHead className="font-bold">
                        Assessed Category
                      </TableHead>
                      <TableHead className="font-bold">
                        Assessed Vendor
                      </TableHead>
                      <TableHead className="font-bold">
                        Rectified Category
                      </TableHead>
                      <TableHead className="font-bold">
                        Rectified Vendor
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingTransactions.map((txn) => (
                      <TableRow key={txn.id}>
                        <TableCell>{txn.date}</TableCell>
                        <TableCell className="break-words max-w-[200px]">
                          {txn.vendor}
                        </TableCell>
                        <TableCell>{txn.amount}</TableCell>
                        <TableCell>{txn.assessed_category}</TableCell>
                        <TableCell>{txn.assessed_vendor}</TableCell>
                        <TableCell>
                          <select
                            id={`category-${txn.id}`}
                            className="rounded-md border border-gray-300 p-2 text-sm w-full"
                            value={txn.rectified_category}
                            onChange={(e) => {
                              rectifyTransaction({
                                ...txn,
                                rectified_category: e.target.value,
                              });
                            }}
                          >
                            <option value=""></option>
                            {categories.map((category) => (
                              <option key={category} value={category}>
                                {category.replace("Expenses:", "")}
                              </option>
                            ))}
                          </select>
                        </TableCell>
                        <TableCell>
                          <input
                            id={`vendor-${txn.id}`}
                            type="text"
                            className="rounded-md border border-gray-300 p-2 text-sm w-full"
                            defaultValue={
                              txn.rectified_vendor || txn.assessed_vendor
                            }
                            onChange={(e) => {
                              rectifyTransaction({
                                ...txn,
                                rectified_vendor: e.target.value,
                              });
                            }}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <div className="flex justify-end mt-6">
                <Button
                  onClick={() => submitFeedback(pendingTransactions)}
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                >
                  Submit
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
