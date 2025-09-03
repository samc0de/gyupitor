import React from 'react';

function Header() {
  return (
    <header className="bg-primary text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">BQ Optimizer</h1>
        <div className="text-sm">
          User: Frank FinOps / Diana Dev
        </div>
      </div>
    </header>
  );
}

export default Header;
