import { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
};

export default function Card({ children, className = "" }: CardProps) {
  return (
    <div className={`rounded-2xl bg-white shadow-lg ${className}`.trim()}>
      {children}
    </div>
  );
}
