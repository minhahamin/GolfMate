import { Link, useParams } from 'react-router-dom';

import Layout from '../components/Layout';
import { useCourse } from '../hooks/useCourses';

export default function CourseDetail() {
  const { id } = useParams();
  const courseId = Number(id);
  const { data: course, isLoading } = useCourse(courseId);

  if (isLoading || !course) {
    return (
      <Layout>
        <p className="text-sm text-ink-soft">불러오는 중...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">{course.name}</h1>
      <p className="mt-1 text-sm text-ink-soft">{course.region}</p>
      {course.address && <p className="text-sm text-ink-soft">{course.address}</p>}
      {course.description && <p className="mt-4 text-sm text-ink-soft">{course.description}</p>}

      <p className="mt-4 font-mono text-sm text-ink-soft">
        {course.holes_count}홀, 파{course.par}
      </p>

      <section className="mt-6 overflow-x-auto border border-ink/15 p-4">
        <table className="w-full min-w-[480px] text-sm">
          <thead>
            <tr className="text-left text-ink-soft">
              <th className="p-2">홀</th>
              <th className="p-2">파</th>
              <th className="p-2">거리 (m)</th>
            </tr>
          </thead>
          <tbody>
            {course.holes.map((hole) => (
              <tr key={hole.hole_number} className="border-t border-ink/10">
                <td className="p-2 font-mono text-ink">{hole.hole_number}</td>
                <td className="p-2 font-mono text-ink-soft">{hole.par}</td>
                <td className="p-2 font-mono text-ink">{hole.distance_meters}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <Link
        to={`/rounds/new`}
        className="mt-6 inline-block bg-flag px-5 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep"
      >
        이 골프장에서 라운드 등록
      </Link>
    </Layout>
  );
}
