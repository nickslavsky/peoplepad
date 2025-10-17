import Header from '@/app/layout/Header'
import SearchPanel from './components/SearchPanel'
import RecordList from './components/RecordList'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { SearchRequest } from '@/lib/api'
import { searchRecords } from '@/lib/api'

export default function DashboardPage() {
  const [searchParams, setSearchParams] = useState<SearchRequest | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['search', searchParams],
    queryFn: () => searchRecords(searchParams!),
    enabled: !!searchParams && (searchParams.query.trim() !== '' || searchParams.tags.length > 0 || !!searchParams.start_date || !!searchParams.end_date),
  })

  return (
    <div>
      <Header />
      <SearchPanel onSearch={setSearchParams} />
      <hr className="border-borderGray" />
      {isLoading ? (
        <div className="p-4">Loading...</div>
      ) : data ? (
        <RecordList records={data} />
      ) : (
        <div className="p-4">Perform a search to see results.</div>
      )}
    </div>
  )
}