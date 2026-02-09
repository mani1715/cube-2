interface StatusBadgeProps {
  status: string;
  variant?: 'default' | 'session' | 'volunteer' | 'contact' | 'event';
}

export const StatusBadge = ({ status, variant = 'default' }: StatusBadgeProps) => {
  const getStatusColor = () => {
    const lowerStatus = status.toLowerCase();
    
    // Session statuses
    if (lowerStatus === 'pending') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (lowerStatus === 'confirmed') return 'bg-green-100 text-green-800 border-green-200';
    if (lowerStatus === 'completed') return 'bg-blue-100 text-blue-800 border-blue-200';
    if (lowerStatus === 'cancelled') return 'bg-red-100 text-red-800 border-red-200';
    
    // Volunteer/general statuses
    if (lowerStatus === 'approved' || lowerStatus === 'active') return 'bg-green-100 text-green-800 border-green-200';
    if (lowerStatus === 'inactive') return 'bg-gray-100 text-gray-800 border-gray-200';
    
    // Contact statuses
    if (lowerStatus === 'new') return 'bg-blue-100 text-blue-800 border-blue-200';
    if (lowerStatus === 'read') return 'bg-purple-100 text-purple-800 border-purple-200';
    if (lowerStatus === 'responded') return 'bg-green-100 text-green-800 border-green-200';
    
    // Event/blog statuses
    if (lowerStatus === 'published') return 'bg-green-100 text-green-800 border-green-200';
    if (lowerStatus === 'draft') return 'bg-gray-100 text-gray-800 border-gray-200';
    
    // Default
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <span
      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusColor()}`}
    >
      {status}
    </span>
  );
};
