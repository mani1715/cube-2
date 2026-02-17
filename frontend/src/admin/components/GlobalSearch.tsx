import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '@/lib/adminApi';

interface SearchResult {
  id: string;
  title?: string;
  full_name?: string;
  email?: string;
  entity: string;
}

const GlobalSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Record<string, any[]>>({});
  const [isSearching, setIsSearching] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const searchRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Debounce timer
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (query.trim().length < 2) {
      setResults({});
      setTotalResults(0);
      setIsOpen(false);
      return;
    }

    debounceTimerRef.current = setTimeout(async () => {
      setIsSearching(true);
      setIsOpen(true);

      try {
        const response = await adminAPI.globalSearch(query);
        setResults(response.results || {});
        setTotalResults(response.total || 0);
      } catch (error) {
        console.error('Search failed:', error);
        setResults({});
        setTotalResults(0);
      } finally {
        setIsSearching(false);
      }
    }, 300); // 300ms debounce

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query]);

  const handleClear = () => {
    setQuery('');
    setResults({});
    setTotalResults(0);
    setIsOpen(false);
  };

  const handleResultClick = (entity: string, id: string) => {
    // Navigate to the appropriate admin page
    const entityRoutes: Record<string, string> = {
      sessions: '/admin/sessions',
      events: '/admin/events',
      blogs: '/admin/blogs',
      psychologists: '/admin/psychologists',
      volunteers: '/admin/volunteers',
      jobs: '/admin/jobs',
      contacts: '/admin/contacts',
    };

    const route = entityRoutes[entity];
    if (route) {
      navigate(route);
      handleClear();
    }
  };

  const getDisplayText = (item: any, entity: string): string => {
    if (item.title) return item.title;
    if (item.full_name) return item.full_name;
    if (item.email) return item.email;
    return `${entity} - ${item.id?.substring(0, 8)}`;
  };

  const getEntityLabel = (entity: string): string => {
    const labels: Record<string, string> = {
      sessions: 'Sessions',
      events: 'Events',
      blogs: 'Blogs',
      psychologists: 'Psychologists',
      volunteers: 'Volunteers',
      jobs: 'Jobs',
      contacts: 'Contacts',
    };
    return labels[entity] || entity;
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-md" data-testid="global-search">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="text"
          placeholder="Search across all entities..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10 pr-10 bg-gray-50 border-gray-200"
          data-testid="global-search-input"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            data-testid="clear-search-btn"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && (
        <div className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-96 overflow-y-auto z-50">
          {isSearching ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
            </div>
          ) : totalResults === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No results found for "{query}"
            </div>
          ) : (
            <div className="py-2">
              <div className="px-4 py-2 text-sm text-gray-500 border-b">
                Found {totalResults} result{totalResults > 1 ? 's' : ''}
              </div>
              {Object.entries(results).map(([entity, items]) => (
                <div key={entity} className="border-b last:border-b-0">
                  <div className="px-4 py-2 text-xs font-semibold text-gray-700 bg-gray-50">
                    {getEntityLabel(entity)} ({items.length})
                  </div>
                  {items.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleResultClick(entity, item.id)}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                      data-testid={`search-result-${entity}-${item.id}`}
                    >
                      <div className="font-medium text-sm text-gray-900">
                        {getDisplayText(item, entity)}
                      </div>
                      {item.email && (
                        <div className="text-xs text-gray-500 mt-1">{item.email}</div>
                      )}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GlobalSearch;
