import { Link } from 'react-router-dom';

import Layout from '../components/Layout';
import { useCourses } from '../hooks/useCourses';

export default function Courses() {
  const { data: courses, isLoading } = useCourses();

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-emerald-50">골프장</h1>
      <p className="mt-1 text-sm text-emerald-200/60">
        지금은 데모용 코스 목록입니다. 실제 골프장 데이터 연동은 이후 Phase에서 추가됩니다.
      </p>

      {isLoading ? (
        <p className="mt-8 text-sm text-emerald-200/60">불러오는 중...</p>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {courses?.map((course) => (
            <Link
              key={course.id}
              to={`/courses/${course.id}`}
              className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6 transition hover:bg-emerald-900/30"
            >
              <p className="text-lg text-emerald-50">{course.name}</p>
              <p className="text-sm text-emerald-200/60">{course.region}</p>
              <p className="mt-3 text-sm text-emerald-200/70">
                {course.holes_count}홀 · 파{course.par}
              </p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
