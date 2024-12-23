"use client";

import { useAgentWorkflow } from "@/hooks/useAgentworkflow";
import { Button } from "@/components/ui/button";
import { LoadingIcon } from '@/components/LoadingIcon';
import { useEffect, useState, useRef } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import TransactionsPage from "@/app/txns/page";
import { LoadingSpinner } from "./LoadingSpinner";

export function TransactionFlowClient() {
  const [isMounted, setIsMounted] = useState(false);
  const [uploadErrorMessage, setuploadErrorMessage] = useState<string | null>(null);
  const [beancountFilepath, setBeancountFilepath] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;
    const file = files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("File upload failed");
      }

      const data = await response.json();
      setBeancountFilepath(data.beancount_filepath);
    } catch (error) {
      console.error("Error uploading file:", error);
      setuploadErrorMessage("Error uploading file");
    }
  };

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Don't render anything until the component is mounted
  if (!isMounted) {
    return null;
  }

  return (
    <div className="p-4">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
      />
      {fileInputRef.current?.files?.[0] ? (
        <div className="mb-4">
          <p className="text-sky-600 pb-5 pr-5 float-left">
            Uploaded File: <span className="font-mono">{fileInputRef.current.files[0].name}</span>
          </p>
          {beancountFilepath && (
            <p className="text-sky-600 pb-5 float-left">
              Beancount Filepath: <span className="font-mono">{beancountFilepath}</span>
            </p>
          )}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded ml-4"
          >
            Change
          </button>
        </div>
      ) : (
        <div>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Upload Statement
          </button>
        </div>
      )}

      {uploadErrorMessage && (
        <div className="mb-4">
          <p className="text-red-600">{uploadErrorMessage}</p>
        </div>
      )}

      {beancountFilepath && (
        <div className="mb-4 clear-both">
          <div className="text-xs font-mono float-right">
            Connection Status: {isConnected ? "Connected" : "Disconnected"}
            {isConnected && (
              <div className="inline-block float-right pl-2">
                <LoadingIcon width={14} height={14} className="text-green-500" />
              </div>
            )}
          </div>
          {!isConnected && currentState !== "completed" && (
            <button
              onClick={() => beancountFilepath && initializeConnection(beancountFilepath)}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Categorize Expenses
            </button>
          )}
          {currentState === "completed" && (
            <div className="place-items-center pt-5">
              <h3 className="text-2xl text-green-700 font-extrabold">
                Categorization is complete 🎉
              </h3>
            </div>
          )}

          {isConnected && (
            <div className="pt-10">
              <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                <div
                  className="bg-green-500 h-4 rounded-full transition-all duration-500"
                  style={{
                    width: progress ? `${(progress.processed / progress.total) * 100}%` : '0%',
                  }}
                ></div>
              </div>
              <div className="text-sky-600 font-bold pt-5">
                All transactions: {progress ? progress.total : <LoadingIcon width={14} height={14} className="text-sky-600 inline-block" />} | Categorized transactions: {progress ? progress.processed : <LoadingIcon width={14} height={14} className="text-sky-600 inline-block" />}
              </div>
            </div>
          )}
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
          {!isConnected && <TransactionsPage beancount_filepath={beancountFilepath} />}
        </div>
      )}
    </div>
  );
}
