export default function CommentaryBlock({ text, generatedBy }: { text: string; generatedBy?: string }) {
  return (
    <div className="card border-t-[3px] border-t-brand p-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="chip bg-brand/15 text-brand2">AI Commentary</span>
        {generatedBy && (
          <span className="text-[10px] text-slate-500">
            {generatedBy === "openai" ? "LLM-generated" : "Rule-based (demo mode)"}
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed text-slate-200">{text}</p>
    </div>
  );
}
