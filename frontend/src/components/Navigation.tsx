"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-gray-800 p-6">
      <div className="flex gap-8">
        <Link
          href="/"
          className={`text-l font-bold ${
            pathname === "/" ? "text-white" : "text-gray-400 hover:text-white"
          }`}
        >
          Home
        </Link>
        <Link
          href="/txns"
          className={`text-l font-bold ${
            pathname === "/txns"
              ? "text-white"
              : "text-gray-400 hover:text-white"
          }`}
        >
          Transactions
        </Link>
      </div>
    </nav>
  );
}
