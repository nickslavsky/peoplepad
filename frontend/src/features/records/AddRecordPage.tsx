import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { addRecord, RecordCreate } from '@/lib/api'
import RecordForm from './components/RecordForm'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'

export default function AddRecordPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: addRecord,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      queryClient.invalidateQueries({ queryKey: ['search'] })
      toast.success('Record added')
      navigate('/dashboard')
    },
    onError: () => toast.error('Error adding record')
  })

  const handleSubmit = (data: RecordCreate) => {
    mutation.mutate(data)
  }

  return (
    <div>
      <div className="flex items-center p-4 border-b border-borderGray">
        <Link to="/dashboard">
          <Button variant="ghost"><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
        </Link>
      </div>
      <h2 className="p-4 text-2xl font-semibold">Add Record</h2>
      <hr className="border-borderGray" />
      <RecordForm onSubmit={handleSubmit} onCancel={() => navigate('/dashboard')} submitLabel="Save" />
    </div>
  )
}