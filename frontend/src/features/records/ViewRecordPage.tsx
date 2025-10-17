import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { getRecord } from '@/lib/api'
import TagChip from '@/features/tags/TagChip'
import { format } from 'date-fns'
import { ArrowLeft, Pencil } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'

export default function ViewRecordPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['record', id],
    queryFn: () => getRecord(id!),
  })

  if (isLoading) return <div className="p-4">Loading...</div>
  if (!data) return <div className="p-4">Not found</div>

  return (
    <div>
      <div className="flex justify-between items-center p-4 border-b border-borderGray">
        <Button variant="ghost" onClick={() => navigate(-1)}><ArrowLeft className="mr-2 h-4 w-4" /> Back to Search</Button>
        <Link to={`/edit/${id}`}>
          <Button><Pencil className="mr-2 h-4 w-4" /> Edit Record</Button>
        </Link>
      </div>
      <h2 className="p-4 text-2xl font-semibold">{data.name}</h2>
      <hr className="border-borderGray" />
      <div className="p-4">
        <h3 className="font-medium">Notes:</h3>
        <p className="text-subtext">{data.notes || 'No notes'}</p>
        <h3 className="font-medium mt-4">Tags:</h3>
        <div className="flex flex-wrap gap-2">
          {data.tags.map(tag => <TagChip key={tag} tag={tag} />)}
        </div>
        <div className="mt-4 text-subtext">
          Created: {format(new Date(data.created_at), 'MMM d, yyyy')}
          <br />
          Modified: {format(new Date(data.updated_at), 'MMM d, yyyy')}
        </div>
      </div>
    </div>
  )
}