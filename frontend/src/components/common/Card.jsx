function Card({ children, className = "", as: Component = "div" }) {
  return (
    <Component className={`rounded-xl border border-shield-line bg-shield-panel/92 shadow-[0_18px_50px_rgba(2,6,23,0.22)] ${className}`}>
      {children}
    </Component>
  );
}

export default Card;
