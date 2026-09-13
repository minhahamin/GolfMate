import { Link } from 'react-router-dom';

import Layout from '../components/Layout';
import { useCourses } from '../hooks/useCourses';

export default function Courses() {
  const { data: courses, isLoading } = useCourses();

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">골프장</h1>
      <p className="mt-1 text-sm text-ink-soft">
        지금은 데모용 코스 목록입니다. 실제 골프장 데이터 연동은 이후 Phase에서 추가됩니다.
      </p>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-soft">불러오는 중...</p>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-px border border-ink/15 bg-ink/15 sm:grid-cols-2">
          {courses?.map((course) => (
            <Link
              key={course.id}
              to={`/courses/${course.id}`}
              className="bg-paper p-6 transition hover:bg-paper-2"
            >
              <p className="font-display text-lg text-ink">{course.name}</p>
              <p className="text-sm text-ink-soft">{course.region}</p>
              <p className="mt-3 font-mono text-sm text-ink-soft">
                {course.holes_count}홀, 파{course.par}
              </p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
