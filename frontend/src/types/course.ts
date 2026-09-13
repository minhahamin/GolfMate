export interface CourseHole {
  hole_number: number;
  par: number;
  distance_meters: number;
}

export interface Course {
  id: number;
  name: string;
  region: string;
  address: string | null;
  description: string | null;
  holes_count: number;
  par: number;
}

export interface CourseDetail extends Course {
  holes: CourseHole[];
}
