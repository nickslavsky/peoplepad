import RecordItem from './RecordItem'
import { SearchResponse } from '@/lib/api'

interface Props {
  records: SearchResponse[]
}

export default function RecordList({ records }: Props) {
  if (records.length === 0) return <p className="p-4">No results found.</p>
  return (
    <div className="p-4">
      <h3 className="font-semibold mb-2">Results (ranked by similarity):</h3>
      {records.map((record, index) => (
        <RecordItem key={record.id} record={record} index={index + 1} />
      ))}
    </div>
  )
}