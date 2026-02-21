import { HistoryList } from "@/components/HistoryList";

export const metadata = {
  title: "計算履歴 | Zeitan",
};

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">計算履歴</h1>
        <p className="text-sm text-muted-foreground">
          過去の損益計算セッションを確認できます
        </p>
      </div>
      <HistoryList />
    </div>
  );
}
