import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { getRecord, updateRecord, RecordUpdate } from '@/lib/api'
import RecordForm from './components/RecordForm'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'

export default function EditRecordPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['record', id],
    queryFn: () => getRecord(id!),
  })

  const mutation = useMutation({
    mutationFn: (data: RecordUpdate) => updateRecord(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      queryClient.invalidateQueries({ queryKey: ['search'] })
      queryClient.invalidateQueries({ queryKey: ['record', id] })
      toast.success('Record updated')
      navigate(`/view/${id}`)
    },
    onError: () => toast.error('Error updating record')
  })

  if (isLoading) return <div className="p-4">Loading...</div>
  if (!data) return <div className="p-4">Not found</div>

  const handleSubmit = (data: RecordUpdate) => {
    mutation.mutate(data)
  }

  return (
    <div>
      <div className="flex items-center p-4 border-b border-borderGray">
        <Link to={`/view/${id}`}>
          <Button variant="ghost"><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
        </Link>
      </div>
      <h2 className="p-4 text-2xl font-semibold">Edit Record</h2>
      <hr className="border-borderGray" />
      <RecordForm defaultValues={data} onSubmit={handleSubmit} onCancel={() => navigate(`/view/${id}`)} submitLabel="Save" />
    </div>
  )
}