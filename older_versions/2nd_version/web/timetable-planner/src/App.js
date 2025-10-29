import React, { useState, useEffect } from 'react';
import { Download, AlertCircle, CheckCircle, AlertTriangle, X, Plus } from 'lucide-react';

// Teacher data from your PDF
const TEACHERS = [
  { id: 'RMA', name: 'Ms. Rashmi Mishra', initials: 'RMA', maxHours: 16 },
  { id: 'RYV', name: 'Ms. Rashmi Yadav', initials: 'RYV', maxHours: 16 },
  { id: 'AGT', name: 'Ms. Archana Gahlaut', initials: 'AGT', maxHours: 16 },
  { id: 'SAL', name: 'Dr. Shalini Aggarwal', initials: 'SAL', maxHours: 16 },
  { id: 'VSD', name: 'Prof. Veer Sain Dixit', initials: 'VSD', maxHours: 16 },
  { id: 'UOA', name: 'Ms. Uma Ojha', initials: 'UOA', maxHours: 16 },
  { id: 'JMN', name: 'Mr. Jag Mohan', initials: 'JMN', maxHours: 16 },
  { id: 'PJN', name: 'Dr. Parul Jain', initials: 'PJN', maxHours: 16 },
  { id: 'DSH', name: 'Mr. Dharmendra Singh', initials: 'DSH', maxHours: 16 },
  { id: 'MYV', name: 'Mr. Manvendra Yadav', initials: 'MYV', maxHours: 16 },
  { id: 'MCN', name: 'Ms. Manisha Chouhan', initials: 'MCN', maxHours: 16 },
  { id: 'LKS', name: 'Dr. Lokesh Kumar Srivastava', initials: 'LKS', maxHours: 16 },
  { id: 'MKR', name: 'Mr. Mahesh Kumar', initials: 'MKR', maxHours: 16 },
  { id: 'RKR', name: 'Dr. Roushan Kumar', initials: 'RKR', maxHours: 16 },
];

// Sample subjects from your PDF
const INITIAL_SUBJECTS = [
  { id: 's1', course: 'CS(H)', semester: 1, name: 'Mathematics for Computing', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 55, department: 'Computer Science' },
  { id: 's2', course: 'CS(H)', semester: 1, name: 'OOPS using python', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 55, department: 'Computer Science' },
  { id: 's3', course: 'CS(H)', semester: 1, name: 'Computer System Architecture', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 55, department: 'Computer Science' },
  { id: 's4', course: 'CS(H)', semester: 3, name: 'Data Structures', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's5', course: 'CS(H)', semester: 3, name: 'Artificial Intelligence', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's6', course: 'CS(H)', semester: 3, name: 'Operating System', type: 'DSC', le: 3, tu: 0, pr: 1, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's7', course: 'CS(H)', semester: 3, name: 'Data Mining', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's8', course: 'CS(P)', semester: 1, name: 'Programming using C++', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 50, department: 'Computer Science' },
  { id: 's9', course: 'CS(P)', semester: 3, name: 'OOPS using Python', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 46, department: 'Computer Science' },
  { id: 's10', course: 'CS(P)', semester: 3, name: 'Design and Analysis of Algo', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 46, department: 'Computer Science' },
];

const TimetablePlanner = () => {
  const [subjects, setSubjects] = useState(INITIAL_SUBJECTS);
  const [assignments, setAssignments] = useState({});
  const [draggedTeacher, setDraggedTeacher] = useState(null);
  const [searchTeacher, setSearchTeacher] = useState('');
  const [searchSubject, setSearchSubject] = useState('');
  const [filterSemester, setFilterSemester] = useState('all');
  const [filterType, setFilterType] = useState('all');

  // Calculate teacher workload
  const getTeacherWorkload = (teacherId) => {
    let totalHours = 0;
    let subjectCount = 0;
    
    Object.entries(assignments).forEach(([subjectId, data]) => {
      if (data.mainTeacher === teacherId) {
        const subject = subjects.find(s => s.id === subjectId);
        if (subject) {
          totalHours += data.assignedLe + data.assignedTu + data.assignedPr;
          subjectCount++;
        }
      }
      if (data.coTeachers?.includes(teacherId)) {
        const subject = subjects.find(s => s.id === subjectId);
        if (subject) {
          // Co-teachers get full hours in co-teaching scenario
          totalHours += data.assignedLe + data.assignedTu + data.assignedPr;
          subjectCount++;
        }
      }
    });
    
    return { totalHours, subjectCount };
  };

  // Get color based on workload
  const getWorkloadColor = (hours, maxHours) => {
    const percentage = (hours / maxHours) * 100;
    if (percentage > 100) return 'bg-red-100 border-red-400 text-red-800';
    if (percentage >= 80) return 'bg-green-100 border-green-400 text-green-800';
    if (percentage >= 50) return 'bg-yellow-100 border-yellow-400 text-yellow-800';
    return 'bg-gray-100 border-gray-300 text-gray-600';
  };

  // Get subject completion status
  const getSubjectStatus = (subject) => {
    const assignment = assignments[subject.id];
    if (!assignment) return { complete: false, hours: 0, total: subject.le + subject.tu + subject.pr };
    
    const assigned = assignment.assignedLe + assignment.assignedTu + assignment.assignedPr;
    const total = subject.le + subject.tu + subject.pr;
    
    return { complete: assigned >= total, hours: assigned, total };
  };

  // Handle drag start
  const handleDragStart = (e, teacher) => {
    setDraggedTeacher(teacher);
    e.dataTransfer.effectAllowed = 'move';
  };

  // Handle drop on subject
  const handleDrop = (e, subjectId) => {
    e.preventDefault();
    if (!draggedTeacher) return;

    const subject = subjects.find(s => s.id === subjectId);
    if (!subject) return;

    // Check if subject already has assignment
    const existingAssignment = assignments[subjectId];
    
    if (!existingAssignment) {
      // New assignment - assign full hours
      setAssignments(prev => ({
        ...prev,
        [subjectId]: {
          mainTeacher: draggedTeacher.id,
          coTeachers: [],
          assignedLe: subject.le,
          assignedTu: subject.tu,
          assignedPr: subject.pr,
        }
      }));
    } else {
      // Subject already assigned - add as co-teacher
      if (existingAssignment.mainTeacher !== draggedTeacher.id && 
          !existingAssignment.coTeachers.includes(draggedTeacher.id)) {
        setAssignments(prev => ({
          ...prev,
          [subjectId]: {
            ...existingAssignment,
            coTeachers: [...existingAssignment.coTeachers, draggedTeacher.id]
          }
        }));
      }
    }
    
    setDraggedTeacher(null);
  };

  // Remove teacher from subject
  const removeTeacher = (subjectId, teacherId, isCoTeacher = false) => {
    if (isCoTeacher) {
      setAssignments(prev => ({
        ...prev,
        [subjectId]: {
          ...prev[subjectId],
          coTeachers: prev[subjectId].coTeachers.filter(id => id !== teacherId)
        }
      }));
    } else {
      // Removing main teacher - clear entire assignment
      const newAssignments = { ...assignments };
      delete newAssignments[subjectId];
      setAssignments(newAssignments);
    }
  };

  // Export to Excel format
  const exportToExcel = () => {
    const rows = [];
    
    subjects.forEach(subject => {
      const assignment = assignments[subject.id];
      if (!assignment) return;

      const teacher = TEACHERS.find(t => t.id === assignment.mainTeacher);
      const coTeacherNames = assignment.coTeachers
        .map(id => TEACHERS.find(t => t.id === id)?.name)
        .filter(Boolean);
      
      const teacherStr = coTeacherNames.length > 0 
        ? `${teacher.name}, ${coTeacherNames.join(', ')}`
        : teacher.name;

      rows.push({
        Course: subject.course,
        Semester: subject.semester,
        Subject: subject.name,
        Section: '',
        Teacher: teacherStr,
        'Hours Taught(Le,Tu,Pr)': `${assignment.assignedLe},${assignment.assignedTu},${assignment.assignedPr}`,
        Department: subject.department,
        Subject_type: subject.type,
        Has_Lab: subject.hasLab ? 'yes' : 'no',
        Notes: ''
      });
    });

    // Create CSV content
    const headers = Object.keys(rows[0] || {});
    const csv = [
      headers.join(','),
      ...rows.map(row => headers.map(h => row[h]).join(','))
    ].join('\n');

    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'timetable_input.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Calculate validation stats
  const getValidationStats = () => {
    const errors = [];
    const warnings = [];
    const success = [];

    // Check teacher overload
    TEACHERS.forEach(teacher => {
      const { totalHours } = getTeacherWorkload(teacher.id);
      if (totalHours > teacher.maxHours) {
        errors.push(`${teacher.name} overloaded: ${totalHours}h/${teacher.maxHours}h`);
      } else if (totalHours >= teacher.maxHours * 0.8) {
        success.push(`${teacher.name}: ${totalHours}h/${teacher.maxHours}h (optimal)`);
      } else if (totalHours < teacher.maxHours * 0.5 && totalHours > 0) {
        warnings.push(`${teacher.name} underutilized: ${totalHours}h/${teacher.maxHours}h`);
      }
    });

    // Check incomplete subjects
    subjects.forEach(subject => {
      const status = getSubjectStatus(subject);
      if (!assignments[subject.id]) {
        errors.push(`${subject.name} (${subject.course} Sem${subject.semester}): No teacher assigned`);
      } else if (status.hours < status.total) {
        warnings.push(`${subject.name}: ${status.hours}h/${status.total}h assigned`);
      }
    });

    return { errors, warnings, success };
  };

  const validation = getValidationStats();

  // Filter teachers and subjects
  const filteredTeachers = TEACHERS.filter(t => 
    t.name.toLowerCase().includes(searchTeacher.toLowerCase()) ||
    t.initials.toLowerCase().includes(searchTeacher.toLowerCase())
  );

  const filteredSubjects = subjects.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(searchSubject.toLowerCase()) ||
                          s.course.toLowerCase().includes(searchSubject.toLowerCase());
    const matchesSemester = filterSemester === 'all' || s.semester === parseInt(filterSemester);
    const matchesType = filterType === 'all' || s.type === filterType;
    return matchesSearch && matchesSemester && matchesType;
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Timetable Planner</h1>
            <button
              onClick={exportToExcel}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Download size={20} />
              Export to CSV
            </button>
          </div>

          {/* Validation Status */}
          <div className="grid grid-cols-3 gap-4">
            <div className="flex items-center gap-2 p-3 bg-red-50 rounded-lg">
              <AlertCircle className="text-red-600" size={20} />
              <div>
                <div className="text-2xl font-bold text-red-600">{validation.errors.length}</div>
                <div className="text-sm text-red-700">Errors</div>
              </div>
            </div>
            <div className="flex items-center gap-2 p-3 bg-yellow-50 rounded-lg">
              <AlertTriangle className="text-yellow-600" size={20} />
              <div>
                <div className="text-2xl font-bold text-yellow-600">{validation.warnings.length}</div>
                <div className="text-sm text-yellow-700">Warnings</div>
              </div>
            </div>
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="text-green-600" size={20} />
              <div>
                <div className="text-2xl font-bold text-green-600">{validation.success.length}</div>
                <div className="text-sm text-green-700">OK</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto grid grid-cols-2 gap-6">
        {/* Teachers Panel */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Teachers</h2>
          <input
            type="text"
            placeholder="Search teachers..."
            value={searchTeacher}
            onChange={(e) => setSearchTeacher(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg mb-4"
          />
          
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {filteredTeachers.map(teacher => {
              const { totalHours, subjectCount } = getTeacherWorkload(teacher.id);
              const colorClass = getWorkloadColor(totalHours, teacher.maxHours);
              
              return (
                <div
                  key={teacher.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, teacher)}
                  className={`p-4 border-2 rounded-lg cursor-move transition-all hover:shadow-md ${colorClass}`}
                >
                  <div className="font-semibold">{teacher.name}</div>
                  <div className="text-sm mt-1">
                    {totalHours}h / {teacher.maxHours}h ({subjectCount} subjects)
                  </div>
                  <div className="text-xs mt-1 opacity-75">{teacher.initials}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Subjects Panel */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Subjects</h2>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="Search subjects..."
              value={searchSubject}
              onChange={(e) => setSearchSubject(e.target.value)}
              className="flex-1 px-4 py-2 border rounded-lg"
            />
            <select
              value={filterSemester}
              onChange={(e) => setFilterSemester(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="all">All Semesters</option>
              <option value="1">Sem 1</option>
              <option value="3">Sem 3</option>
              <option value="5">Sem 5</option>
              <option value="7">Sem 7</option>
            </select>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="all">All Types</option>
              <option value="DSC">DSC</option>
              <option value="DSE">DSE</option>
              <option value="GE">GE</option>
              <option value="SEC">SEC</option>
            </select>
          </div>

          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {filteredSubjects.map(subject => {
              const assignment = assignments[subject.id];
              const status = getSubjectStatus(subject);
              const isComplete = status.complete;
              
              return (
                <div
                  key={subject.id}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => handleDrop(e, subject.id)}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    isComplete 
                      ? 'border-green-400 bg-green-50' 
                      : assignment 
                        ? 'border-yellow-400 bg-yellow-50'
                        : 'border-gray-300 bg-white hover:border-blue-400'
                  }`}
                >
                  <div className="font-semibold">{subject.name}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    {subject.course} Sem{subject.semester} • {subject.type}
                  </div>
                  <div className="text-sm mt-1">
                    {subject.le}L + {subject.tu}T + {subject.pr}P ({status.hours}/{status.total}h)
                  </div>
                  <div className="text-sm text-gray-600">👥 {subject.students} students</div>
                  
                  {assignment && (
                    <div className="mt-3 space-y-2">
                      <div className="flex items-center justify-between p-2 bg-white rounded border">
                        <span className="text-sm font-medium">
                          {TEACHERS.find(t => t.id === assignment.mainTeacher)?.name}
                        </span>
                        <button
                          onClick={() => removeTeacher(subject.id, assignment.mainTeacher)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <X size={16} />
                        </button>
                      </div>
                      
                      {assignment.coTeachers.map(coTeacherId => (
                        <div key={coTeacherId} className="flex items-center justify-between p-2 bg-blue-50 rounded border border-blue-200">
                          <span className="text-sm">
                            {TEACHERS.find(t => t.id === coTeacherId)?.name} (Co-teacher)
                          </span>
                          <button
                            onClick={() => removeTeacher(subject.id, coTeacherId, true)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Validation Details */}
      {(validation.errors.length > 0 || validation.warnings.length > 0) && (
        <div className="max-w-7xl mx-auto mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4">Validation Details</h3>
          
          {validation.errors.length > 0 && (
            <div className="mb-4">
              <div className="font-semibold text-red-600 mb-2">❌ Errors:</div>
              <ul className="space-y-1">
                {validation.errors.slice(0, 10).map((error, i) => (
                  <li key={i} className="text-sm text-red-700">• {error}</li>
                ))}
                {validation.errors.length > 10 && (
                  <li className="text-sm text-red-600 italic">... and {validation.errors.length - 10} more</li>
                )}
              </ul>
            </div>
          )}
          
          {validation.warnings.length > 0 && (
            <div>
              <div className="font-semibold text-yellow-600 mb-2">⚠️ Warnings:</div>
              <ul className="space-y-1">
                {validation.warnings.slice(0, 10).map((warning, i) => (
                  <li key={i} className="text-sm text-yellow-700">• {warning}</li>
                ))}
                {validation.warnings.length > 10 && (
                  <li className="text-sm text-yellow-600 italic">... and {validation.warnings.length - 10} more</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TimetablePlanner;