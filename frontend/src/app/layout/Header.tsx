import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { useAuth } from '@/app/providers/AuthProvider'

export default function Header() {
  const { logout } = useAuth()
  return (
    <header className="flex items-center justify-between p-4 bg-white border-b border-borderGray">
      <Link to="/dashboard" className="text-xl font-bold text-primary">PeoplePad</Link>
      <div className="flex items-center gap-4">
        <Link to="/add">
          <Button>+ Add Record</Button>
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Avatar>
              <AvatarImage src="https://github.com/shadcn.png" />
              <AvatarFallback>U</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={logout}>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}