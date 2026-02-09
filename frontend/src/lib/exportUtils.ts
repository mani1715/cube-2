/**
 * Export utilities for converting data to CSV and downloading files
 */

/**
 * Convert array of objects to CSV string
 */
export const convertToCSV = (data: any[], headers?: string[]): string => {
  if (!data || data.length === 0) {
    return '';
  }

  // Use provided headers or extract from first object
  const csvHeaders = headers || Object.keys(data[0]);
  
  // Create header row
  const headerRow = csvHeaders.join(',');
  
  // Create data rows
  const dataRows = data.map(row => {
    return csvHeaders.map(header => {
      const value = row[header];
      
      // Handle different data types
      if (value === null || value === undefined) {
        return '';
      }
      
      // Convert arrays to string
      if (Array.isArray(value)) {
        return `"${value.join('; ')}"`;
      }
      
      // Convert objects to JSON string
      if (typeof value === 'object') {
        return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
      }
      
      // Escape commas and quotes in strings
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      
      return stringValue;
    }).join(',');
  });
  
  return [headerRow, ...dataRows].join('\n');
};

/**
 * Download data as CSV file
 */
export const downloadCSV = (data: any[], filename: string, headers?: string[]): void => {
  const csv = convertToCSV(data, headers);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  downloadBlob(blob, filename);
};

/**
 * Download blob as file
 */
export const downloadBlob = (blob: Blob, filename: string): void => {
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up the URL
  URL.revokeObjectURL(url);
};

/**
 * Download JSON as file
 */
export const downloadJSON = (data: any, filename: string): void => {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json;charset=utf-8;' });
  downloadBlob(blob, filename);
};

/**
 * Format filename with timestamp
 */
export const formatFilename = (base: string, extension: string = 'csv'): string => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  return `${base}_${timestamp}.${extension}`;
};

/**
 * Clean data for export by removing sensitive fields
 */
export const cleanDataForExport = (data: any[], sensitiveFields: string[] = []): any[] => {
  const defaultSensitiveFields = ['password', 'hashed_password', 'token', 'secret'];
  const fieldsToRemove = [...defaultSensitiveFields, ...sensitiveFields];
  
  return data.map(item => {
    const cleaned = { ...item };
    fieldsToRemove.forEach(field => {
      delete cleaned[field];
    });
    return cleaned;
  });
};
