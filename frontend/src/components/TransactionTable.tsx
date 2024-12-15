import { Transaction } from "@/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

interface Props {
  categories: string[];
  transactions: Transaction[];
  onSubmit: (transactions: Transaction[]) => void;
  onUpdateCategory: (transaction: Transaction) => void;
}

export function TransactionTable({
  categories,
  transactions,
  onSubmit,
  onUpdateCategory,
}: Props) {
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Vendor</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Assessed Category</TableHead>
            <TableHead>Assessed Vendor</TableHead>
            <TableHead>Rectified Category</TableHead>
            <TableHead>Rectified Vendor</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactions.map((transaction) => (
            <TableRow key={transaction.id}>
              <TableCell>{transaction.date}</TableCell>
              <TableCell>{transaction.vendor}</TableCell>
              <TableCell>${transaction.amount.toFixed(2)}</TableCell>
              <TableCell>{transaction.assessed_category}</TableCell>
              <TableCell>{transaction.assessed_vendor}</TableCell>
              <TableCell>
                <Select
                  value={transaction.rectified_category}
                  onValueChange={(value) => {
                    onUpdateCategory({
                      ...transaction,
                      rectified_category: value,
                    });
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </TableCell>
              <TableCell>
                <input
                  type="text"
                  value={transaction.rectified_vendor || ""}
                  onChange={(e) => {
                    onUpdateCategory({
                      ...transaction,
                      rectified_vendor: e.target.value,
                    });
                  }}
                  className="w-full px-2 py-1 border rounded"
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="flex justify-end">
        <Button onClick={() => onSubmit(transactions)}>
          Submit Categories
        </Button>
      </div>
    </div>
  );
}
