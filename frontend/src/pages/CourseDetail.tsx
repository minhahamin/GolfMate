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
        <p className="text-sm text-emerald-200/60">불러오는 중...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-emerald-50">{course.name}</h1>
      <p className="mt-1 text-sm text-emerald-200/60">{course.region}</p>
      {course.address && <p className="text-sm text-emerald-200/50">{course.address}</p>}
      {course.description && (
        <p className="mt-4 text-sm text-emerald-200/80">{course.description}</p>
      )}

      <p className="mt-4 text-sm text-emerald-200/70">
        {course.holes_count}홀 · 파{course.par}
      </p>

      <section className="mt-6 overflow-x-auto rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-4">
        <table className="w-full min-w-[480px] text-sm">
          <thead>
            <tr className="text-left text-emerald-300/70">
              <th className="p-2">홀</th>
              <th className="p-2">파</th>
              <th className="p-2">거리 (m)</th>
            </tr>
          </thead>
          <tbody>
            {course.holes.map((hole) => (
              <tr key={hole.hole_number} className="border-t border-emerald-900/50">
                <td className="p-2 text-emerald-100">{hole.hole_number}</td>
                <td className="p-2 text-emerald-200/70">{hole.par}</td>
                <td className="p-2 text-emerald-50">{hole.distance_meters}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <Link
        to={`/rounds/new`}
        className="mt-6 inline-block rounded-lg bg-emerald-500 px-5 py-2 text-sm font-medium text-emerald-950 transition hover:bg-emerald-400"
      >
        이 골프장에서 라운드 등록
      </Link>
    </Layout>
  );
}
