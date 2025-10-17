import { Link } from 'react-router-dom'
import TagChip from '@/features/tags/TagChip'
import { format } from 'date-fns'
import { SearchResponse } from '@/lib/api'

interface Props {
  record: SearchResponse
  index: number
}

export default function RecordItem({ record, index }: Props) {
  return (
    <div className="border-b border-borderGray py-2 last:border-b-0">
      <div className="flex items-center gap-2">
        <span className="font-medium">{index}. {record.name}</span>
        <span className="text-subtext"> | Notes: {record.notes?.substring(0, 50) || ''}...</span>
      </div>
      <div className="flex flex-wrap gap-1 mt-1">
        Tags: {record.tags.map(tag => <TagChip key={tag} tag={tag} />)}
      </div>
      <div className="text-subtext text-sm mt-1">Last Modified: {format(new Date(record.updated_at), 'MMM d, yyyy')}</div>
      <Link to={`/view/${record.id}`} className="text-primary hover:underline text-sm">View</Link>
    </div>
  )
}