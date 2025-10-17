import { Badge } from '@/components/ui/badge'
import { X } from 'lucide-react'

interface Props {
  tag: string
  onRemove?: () => void
}

export default function TagChip({ tag, onRemove }: Props) {
  return (
    <Badge variant="secondary" className="bg-tagBlue text-primary flex items-center gap-1">
      {tag}
      {onRemove && <X className="h-3 w-3 cursor-pointer" onClick={onRemove} />}
    </Badge>
  )
}