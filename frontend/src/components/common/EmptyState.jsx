import { UploadCloud } from "lucide-react";

import Button from "./Button.jsx";
import Card from "./Card.jsx";

function EmptyState({ title, text, actionLabel, actionHref = "#/upload", icon: Icon = UploadCloud }) {
  return (
    <Card className="p-8 text-center">
      <Icon className="mx-auto text-shield-cyan" size={42} />
      <h2 className="mt-4 text-xl font-semibold text-white">{title}</h2>
      {text && <p className="mx-auto mt-2 max-w-xl text-slate-400">{text}</p>}
      {actionLabel && (
        <Button className="mt-5" onClick={() => {
          window.location.hash = actionHref;
        }}>
          {actionLabel}
        </Button>
      )}
    </Card>
  );
}

export default EmptyState;
