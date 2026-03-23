export function LandingFooter() {
  return (
    <footer className="border-t bg-slate-50 py-8">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            Zeitan &copy; {new Date().getFullYear()}
          </p>
          <div className="flex gap-6 text-sm text-slate-500">
            <span>暗号資産税金計算ツール</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
