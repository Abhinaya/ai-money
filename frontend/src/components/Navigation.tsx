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
          className={`text-2xl font-bold ${pathname === "/" ? "text-white" : "text-gray-400 hover:text-white"
            }`}
        >
          🤖 AI Money
        </Link>
      </div>
    </nav>
  );
}
