import React from 'react';

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
}

export function Table<T extends { id: number | string }>({
  columns,
  data,
  onRowClick,
  emptyMessage = 'No data available',
}: TableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-8 text-center">
        <p className="text-gray-500 font-mono">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#1a1a1a]">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-4 py-3 text-left text-xs font-mono font-semibold text-green-500 uppercase tracking-wider ${
                    col.className || ''
                  }`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr
                key={item.id}
                onClick={() => onRowClick?.(item)}
                className={`border-b border-[#1a1a1a] last:border-b-0 ${
                  onRowClick ? 'cursor-pointer hover:bg-[#111]' : ''
                } ${index % 2 === 0 ? 'bg-[#0a0a0a]' : 'bg-[#080808]'}`}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={`px-4 py-3 text-sm text-gray-300 ${col.className || ''}`}
                  >
                    {col.render
                      ? col.render(item)
                      : String((item as Record<string, unknown>)[col.key] ?? '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
