"use client";

import { useState } from "react";

interface Question {
  id: string;
  type: string;
  title: string;
  description: string;
  difficulty: string;
  tags: string[];
  test_cases?: Array<{ input: string; output: string }>;
  options?: string[];
  correct_answer?: string;
}

interface GeneratedTest {
  test_id: string;
  title: string;
  description: string;
  questions: Question[];
}

export default function Home() {
  const [syllabus, setSyllabus] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [numQuestions, setNumQuestions] = useState(5);
  const [numMcqs, setNumMcqs] = useState(3);
  const [generatedTest, setGeneratedTest] = useState<GeneratedTest | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("python");
  const [code, setCode] = useState("");

  const handleGenerateTest = async () => {
    setLoading(true);
    try {
      const topics = syllabus.split(",").map((t) => t.trim()).filter(Boolean);
      
      const response = await fetch("http://localhost:8000/api/tests/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topics,
          difficulty,
          num_questions: numQuestions,
          num_mcqs: numMcqs,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedTest(data);
      }
    } catch (error) {
      console.error("Failed to generate test:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCodeSubmit = async (questionId: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: selectedLanguage,
          code: code,
          problem_id: questionId,
        }),
      });

      const result = await response.json();
      alert(`Execution Status: ${result.status}\n\nOutput:\n${result.output}`);
    } catch (error) {
      console.error("Failed to execute code:", error);
      alert("Failed to execute code");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            🎓 AI-Powered DSA Learning Platform
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-300">
            Generate custom practice tests powered by AI
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Syllabus Input Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            📚 Create Your Practice Test
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Enter Topics (comma-separated)
              </label>
              <textarea
                value={syllabus}
                onChange={(e) => setSyllabus(e.target.value)}
                placeholder="e.g., Arrays, Linked Lists, Binary Search Trees, Dynamic Programming, Graphs"
                className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Difficulty Level
                </label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Number of Coding Questions
                </label>
                <input
                  type="number"
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(Number(e.target.value))}
                  min="1"
                  max="20"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Number of MCQs
                </label>
                <input
                  type="number"
                  value={numMcqs}
                  onChange={(e) => setNumMcqs(Number(e.target.value))}
                  min="0"
                  max="10"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerateTest}
            disabled={loading || !syllabus.trim()}
            className="mt-6 w-full md:w-auto px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-md transition-colors"
          >
            {loading ? "⏳ Generating Test..." : "🚀 Generate Practice Test"}
          </button>
        </section>

        {/* Generated Test Section */}
        {generatedTest && (
          <section className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {generatedTest.title}
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                {generatedTest.description}
              </p>
              <div className="mt-4 flex gap-4 text-sm">
                <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                  {generatedTest.questions.filter(q => q.type === "coding").length} Coding Questions
                </span>
                <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                  {generatedTest.questions.filter(q => q.type === "mcq").length} MCQs
                </span>
              </div>
            </div>

            {/* Questions */}
            {generatedTest.questions.map((question, index) => (
              <div
                key={question.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Question {index + 1}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-1">
                      {question.title}
                    </h3>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      question.difficulty === "easy"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        : question.difficulty === "medium"
                        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                        : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                    }`}
                  >
                    {question.difficulty}
                  </span>
                </div>

                <div className="prose dark:prose-invert max-w-none mb-4">
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">
                    {question.description}
                  </p>
                </div>

                {/* Test Cases for Coding Questions */}
                {question.type === "coding" && question.test_cases && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                      Test Cases:
                    </h4>
                    <div className="space-y-2">
                      {question.test_cases.map((tc, i) => (
                        <div
                          key={i}
                          className="bg-gray-50 dark:bg-gray-700 rounded p-3 text-sm"
                        >
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Input:</span>
                              <pre className="mt-1 text-gray-900 dark:text-white bg-white dark:bg-gray-800 p-2 rounded overflow-x-auto">
                                {tc.input}
                              </pre>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Expected Output:</span>
                              <pre className="mt-1 text-gray-900 dark:text-white bg-white dark:bg-gray-800 p-2 rounded overflow-x-auto">
                                {tc.output}
                              </pre>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* MCQ Options */}
                {question.type === "mcq" && question.options && (
                  <div className="mb-4 space-y-2">
                    {question.options.map((option, i) => (
                      <label
                        key={i}
                        className="flex items-center p-3 border border-gray-300 dark:border-gray-600 rounded-md cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
                      >
                        <input
                          type="radio"
                          name={`mcq-${question.id}`}
                          className="mr-3"
                        />
                        <span className="text-gray-700 dark:text-gray-300">{option}</span>
                      </label>
                    ))}
                  </div>
                )}

                {/* Code Editor for Coding Questions */}
                {question.type === "coding" && (
                  <div className="mt-4">
                    <div className="flex items-center gap-4 mb-3">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Language:
                      </label>
                      <select
                        value={selectedLanguage}
                        onChange={(e) => setSelectedLanguage(e.target.value)}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      >
                        <option value="python">Python</option>
                        <option value="cpp">C++</option>
                        <option value="java">Java</option>
                        <option value="bash">Bash</option>
                      </select>
                    </div>

                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="// Write your solution here..."
                      className="w-full h-48 px-3 py-2 font-mono text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
                    />

                    <button
                      onClick={() => handleCodeSubmit(question.id)}
                      className="mt-3 px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
                    >
                      ▶️ Run Code
                    </button>
                  </div>
                )}

                {/* Tags */}
                <div className="mt-4 flex flex-wrap gap-2">
                  {question.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </section>
        )}

        {/* Features Section */}
        {!generatedTest && (
          <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                AI-Powered Generation
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Automatically generate customized DSA problems based on your syllabus using advanced AI models.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">🌐</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Web Scraping
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Aggregates content from GeeksforGeeks, Codeforces, and other educational resources.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">💻</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Multi-Language Support
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Write and execute solutions in Python, C++, Java, or Bash with secure sandboxed execution.
              </p>
            </div>
          </section>
        )}
      </main>

      <footer className="mt-16 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <p className="text-center text-gray-600 dark:text-gray-400">
            AI-Powered DSA Learning Platform • Built with Next.js & FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}
