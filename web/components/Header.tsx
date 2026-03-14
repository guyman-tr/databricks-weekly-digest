import Link from "next/link";

export default function Header() {
  return (
    <header className="border-b border-white/10 bg-brand-dark/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-orange to-brand-red flex items-center justify-center font-bold text-white text-sm">
            DW
          </div>
          <div>
            <h1 className="text-white font-semibold text-lg leading-tight group-hover:text-brand-orange transition-colors">
              Databricks Weekly
            </h1>
            <p className="text-brand-muted text-xs">Platform digest & podcast</p>
          </div>
        </Link>
      </div>
    </header>
  );
}
