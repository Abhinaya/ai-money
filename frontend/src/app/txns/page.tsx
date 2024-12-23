"use client";

import { useState, useEffect } from "react";
import { Table, Button, message } from "antd";

interface Posting {
  account: string;
  amount: string;
}

interface Transaction {
  id: string;
  date: string;
  payee: string;
  narration: string;
  from_account: string;
  to_account: string;
  amount: string;
  postings: Posting[];
}

export default function TransactionsPage({ beancount_filepath }: { beancount_filepath?: string }) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactions();
  }, [beancount_filepath]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const url = new URL("http://localhost:8000/api/transactions");
      if (beancount_filepath) {
        url.searchParams.append("beancount_filepath", beancount_filepath);
      }
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTransactions(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching transactions:", error);
      message.error("Failed to load transactions");
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: "Date",
      dataIndex: "date",
      key: "date",
      width: 120,
      sorter: (a: Transaction, b: Transaction) =>
        new Date(a.date).getTime() - new Date(b.date).getTime(),
    },
    {
      title: "Payee",
      dataIndex: "payee",
      key: "payee",
      width: 300,
    },
    {
      title: "From account",
      dataIndex: "from_account",
      key: "from_account",
      width: 300,
    },
    {
      title: "To account",
      dataIndex: "to_account",
      key: "to_account",
      width: 300,
    },
    {
      title: "Amount",
      dataIndex: "amount",
      key: "amount",
      width: 300,
    },
  ];

  return (
    <div className="p-4">
      <div className="flex justify-between mb-4">
        <h1 className="text-2xl font-bold">Transactions</h1>
      </div>

      <Table
        dataSource={transactions}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ defaultPageSize: 10 }}
        size="middle"
        scroll={{ x: true }}
      />
    </div>
  );
}
