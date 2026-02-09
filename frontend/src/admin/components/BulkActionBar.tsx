import React from 'react';
import { Button } from '@/components/ui/button';
import { Trash2, X, Download } from 'lucide-react';

interface BulkActionBarProps {
  selectedCount: number;
  onClearSelection: () => void;
  onBulkDelete: () => void;
  onBulkExport?: () => void;
  entityName: string;
  canDelete?: boolean;
  canExport?: boolean;
}

const BulkActionBar: React.FC<BulkActionBarProps> = ({
  selectedCount,
  onClearSelection,
  onBulkDelete,
  onBulkExport,
  entityName,
  canDelete = true,
  canExport = true,
}) => {
  if (selectedCount === 0) return null;

  return (
    <div 
      className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 bg-gray-900 text-white rounded-lg shadow-2xl px-6 py-4 flex items-center gap-4"
      data-testid="bulk-action-bar"
    >
      <div className="flex items-center gap-2">
        <span className="font-medium" data-testid="selected-count">
          {selectedCount} {entityName}{selectedCount > 1 ? 's' : ''} selected
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        {canDelete && (
          <Button
            variant="destructive"
            size="sm"
            onClick={onBulkDelete}
            className="flex items-center gap-2"
            data-testid="bulk-delete-btn"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </Button>
        )}
        
        {canExport && onBulkExport && (
          <Button
            variant="secondary"
            size="sm"
            onClick={onBulkExport}
            className="flex items-center gap-2"
            data-testid="bulk-export-btn"
          >
            <Download className="h-4 w-4" />
            Export
          </Button>
        )}
        
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearSelection}
          className="flex items-center gap-2 text-white hover:text-white hover:bg-gray-800"
          data-testid="clear-selection-btn"
        >
          <X className="h-4 w-4" />
          Clear
        </Button>
      </div>
    </div>
  );
};

export default BulkActionBar;
