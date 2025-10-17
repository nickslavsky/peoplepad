import { useForm, Controller } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import TagAutocomplete from '@/features/tags/TagAutocomplete'
import { RecordCreate } from '@/lib/api'
import { useTags } from '../../tags/hooks/useTags'

interface Props {
  defaultValues?: Partial<RecordCreate>
  onSubmit: (data: RecordCreate) => void
  onCancel: () => void
  submitLabel: string
}

export default function RecordForm({ defaultValues = {}, onSubmit, onCancel, submitLabel }: Props) {
  const { register, handleSubmit, control } = useForm<RecordCreate>({
    defaultValues: { name: '', notes: '', tags: [], ...defaultValues }
  })
  const tagsQuery = useTags()

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-4">
      <div>
        <Label htmlFor="name">Name</Label>
        <Input id="name" {...register('name', { required: true })} placeholder="Name" />
      </div>
      <div>
        <Label htmlFor="notes">Notes</Label>
        <Textarea id="notes" {...register('notes')} placeholder="Notes" />
      </div>
      <div>
        <Label>Tags</Label>
        <Controller
          control={control}
          name="tags"
          render={({ field }) => (
            <TagAutocomplete
              suggestions={tagsQuery.data ?? []}
              selected={field.value}
              onChange={field.onChange}
              allowCreate={true}
            />
          )}
        />
      </div>
      <div className="flex gap-2">
        <Button type="submit">{submitLabel}</Button>
        <Button variant="secondary" type="button" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  )
}