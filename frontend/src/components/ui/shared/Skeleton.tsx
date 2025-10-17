// src/components/ui/shared/Skeleton.tsx
import React from 'react';

interface SkeletonProps {
  count?: number;
}

const Skeleton: React.FC<SkeletonProps> = ({ count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="p-4 border rounded mb-4 animate-pulse">
          <div className="h-5 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-1"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      ))}
    </>
  );
};

export default Skeleton;