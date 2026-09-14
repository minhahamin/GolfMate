export interface GroupRead {
  id: number;
  name: string;
  owner_id: number;
  created_at: string;
}

export interface GroupMember {
  user_id: number;
  name: string;
  email: string;
  joined_at: string;
}

export interface GroupDetail extends GroupRead {
  members: GroupMember[];
}
