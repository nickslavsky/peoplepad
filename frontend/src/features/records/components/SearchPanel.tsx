import { useForm, Controller } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import TagAutocomplete from '@/features/tags/TagAutocomplete'
import { useTags } from '../../tags/hooks/useTags'
import { SearchRequest } from '@/lib/api'

interface Props {
  onSearch: (data: SearchRequest) => void
}

export default function SearchPanel({ onSearch }: Props) {
  const { register, handleSubmit, setValue, watch } = useForm<SearchRequest>({
    defaultValues: { query: '', tags: [], start_date: undefined, end_date: undefined }
  })
  const tagsQuery = useTags()

  const onSubmit = (data: SearchRequest) => {
    onSearch(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-4">
      <div>
        <Label htmlFor="query">Search</Label>
        <Input id="query" {...register('query')} placeholder="Search text input..." />
      </div>
      <div className="flex flex-wrap gap-4">
        <div>
          <Label>Tag filter</Label>
          <Controller
            name="tags"
            control={useForm().control} // wait, use the form's control
            render={({ field }) => (
              <TagAutocomplete
                suggestions={tagsQuery.data ?? []}
                selected={field.value}
                onChange={field.onChange}
                allowCreate={false}
              />
            )}
          />
        </div>
        <div>
          <Label>From date</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className={cn("w-[240px] justify-start text-left font-normal", !watch('start_date') && "text-subtext")}>
                <CalendarIcon className="mr-2 h-4 w-4" />
                {watch('start_date') ? format(new Date(watch('start_date')), "PPP") : <span>Pick a date</span>}
              </Button>
            </PopoverTrigger>
            <PopoverContent>
              <Calendar
                mode="single"
                selected={watch('start_date') ? new Date(watch('start_date')) : undefined}
                onSelect={(date) => setValue('start_date', date ? date.toISOString() : undefined)}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </div>
        <div>
          <Label>To date</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className={cn("w-[240px] justify-start text-left font-normal", !watch('end_date') && "text-subtext")}>
                <CalendarIcon className="mr-2 h-4 w-4" />
                {watch('end_date') ? format(new Date(watch('end_date')), "PPP") : <span>Pick a date</span>}
              </Button>
            </PopoverTrigger>
            <PopoverContent>
              <Calendar
                mode="single"
                selected={watch('end_date') ? new Date(watch('end_date')) : undefined}
                onSelect={(date) => setValue('end_date', date ? date.toISOString() : undefined)}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>
      <Button type="submit">Search</Button>
    </form>
  )
}