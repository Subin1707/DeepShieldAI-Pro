function Button({ children, className = "", variant = "primary", as: Component = "button", ...props }) {
  const variants = {
    primary: "bg-cyan-400 text-slate-950 hover:bg-cyan-300",
    secondary: "border border-slate-700 bg-slate-950/50 text-slate-200 hover:border-cyan-400/50 hover:text-white",
    ghost: "text-slate-300 hover:bg-slate-800/80 hover:text-white",
  };

  return (
    <Component
      type={Component === "button" ? "button" : undefined}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export default Button;
