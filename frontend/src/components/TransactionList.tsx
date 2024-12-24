"use client";

import { useState, useEffect } from "react";
import { Table, message } from "antd";
import { Bar } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement } from 'chart.js';
Chart.register(CategoryScale, LinearScale, BarElement);

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
    const [categories, setCategories] = useState<string[]>([]);
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
            setTransactions(data.transactions);
            setCategories(data.categories);
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
            dataIndex: "display_amount",
            key: "display_amount",
            width: 300,
        },
    ];

    const getTotalByCategory = (transactions: Transaction[]) => {
        const totals: { [key: string]: number } = {};
        categories.forEach(category => {
            totals[category] = 0;
        });

        transactions.forEach(transaction => {
            if (totals.hasOwnProperty(transaction.to_account)) {
                totals[transaction.to_account] += parseFloat(transaction.amount);
            }
        });

        return totals;
    };
    const totals = getTotalByCategory(transactions);
    const chart_data = {
        labels: categories.map(category => category.replace("Expenses:", "")),
        datasets: [
            {
                label: 'Total Value',
                data: categories.map(category => totals[category]),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            },
        ],
    };

    return (
        <div className="p-4">
            <div className="flex justify-between mb-4">
                <h1 className="text-2xl font-bold">Transactions</h1>
            </div>
            <div className="flex">
                <div className="w-1/2 p-4">
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
                <div className="w-1/2 p-4">
                    <h2 className="text-xl font-bold mb-4">Expenses by Category</h2>
                    <Bar data={chart_data} />
                </div>
            </div>
        </div>
    );
}
