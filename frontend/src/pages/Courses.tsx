import { Link } from 'react-router-dom';

import Layout from '../components/Layout';
import { useCourses } from '../hooks/useCourses';

export default function Courses() {
  const { data: courses, isLoading, isError, refetch } = useCourses();

  return (
    <Layout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl text-ink">골프장</h1>
          <p className="mt-1 text-sm text-ink-soft">
            등록된 코스{courses ? ` ${courses.length}곳` : ''}입니다. AI 추천도 이 목록 안에서 골라줍니다.
          </p>
        </div>
        <Link
          to="/courses/recommend"
          className="bg-flag px-4 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep"
        >
          🤖 AI 추천받기
        </Link>
      </div>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-soft">불러오는 중...</p>
      ) : isError ? (
        <div className="mt-8">
          <p className="text-sm text-flag">골프장 목록을 불러오지 못했습니다.</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-3 border border-ink/20 px-4 py-2 text-sm text-ink transition hover:bg-paper-2"
          >
            다시 시도
          </button>
        </div>
      ) : courses?.length === 0 ? (
        <p className="mt-8 text-sm text-ink-soft">등록된 골프장이 없습니다.</p>
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
                {course.holes_count}홀, 파{course.par}{course.difficulty && ` · 난이도 ${course.difficulty}`}
              </p>
              {course.green_fee_avg != null && (
                <p className="mt-1 font-mono text-sm text-ink-soft">
                  평균 그린피 {course.green_fee_avg.toLocaleString()}원
                </p>
              )}
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
