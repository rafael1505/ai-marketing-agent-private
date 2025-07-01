import React from 'react';
import Image from 'next/image';
import { useImageLoader } from '@/hooks/useImageLoader';

interface CompanyLogoProps {
  logoUrl?: string;
  fallbackUrl?: string;
}

/**
 * CompanyLogo component that safely uses the useImageLoader hook
 * and handles the image display and loading states
 */
export const CompanyLogo: React.FC<CompanyLogoProps> = ({
  logoUrl,
  fallbackUrl = '/placeholder-logo.svg'
}) => {
  // Add cache-busting query param to avoid stale images
  const processedLogoUrl = logoUrl && !logoUrl.startsWith('blob:') 
    ? `${logoUrl}?t=${new Date().getTime()}` 
    : logoUrl;
    
  const { imageUrl, isLoading, error } = useImageLoader(processedLogoUrl, fallbackUrl);
  
  // Check if we have a valid URL to display
  const isEmpty = !logoUrl || logoUrl === '';
  const isErrorAndNotBlob = error && !logoUrl?.startsWith('blob:');
  
  if (isEmpty || isErrorAndNotBlob) {
    // Show placeholder if no logo or if there's an error with a non-blob URL
    return (
      <div className="h-16 border border-dashed border-gray-300 rounded flex items-center justify-center text-gray-400">
        <span>No logo uploaded</span>
      </div>
    );
  }
  
  return (
    <div className="relative h-16">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
          <div className="w-6 h-6 border-2 border-gray-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
      )}
      <Image
        src={imageUrl}
        alt="Company Logo"
        width={150}
        height={64}
        className={`h-16 object-contain border border-gray-200 rounded p-1 transition-opacity duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        priority={true}
        unoptimized={logoUrl?.startsWith('blob:')}
      />
    </div>
  );
};
