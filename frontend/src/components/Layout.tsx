// Layout.tsx
import Header from './Header';
import { type ReactNode } from 'react';

type Props = {
  children: ReactNode;
};

const Layout = ({ children }: Props) => {
  return (
    <>
      <Header />
      <main className="container mt-4">
        {children}
      </main>
    </>
  );
};

export default Layout;
