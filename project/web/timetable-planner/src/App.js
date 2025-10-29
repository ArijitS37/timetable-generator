import React, { useState, useEffect } from 'react';
import { Download, AlertCircle, CheckCircle, AlertTriangle, X, Lock, Unlock, Calendar, Save, RotateCcw, Eye, EyeOff } from 'lucide-react';

// Full teacher data
const TEACHERS = [
  { id: 'RMA', name: 'Ms. Rashmi Mishra', initials: 'RMA', maxHours: 16, department: 'Computer Science' },
  { id: 'RYV', name: 'Ms. Rashmi Yadav', initials: 'RYV', maxHours: 16, department: 'Computer Science' },
  { id: 'AGT', name: 'Ms. Archana Gahlaut', initials: 'AGT', maxHours: 16, department: 'Computer Science' },
  { id: 'SAL', name: 'Dr. Shalini Aggarwal', initials: 'SAL', maxHours: 16, department: 'Computer Science' },
  { id: 'VSD', name: 'Prof. Veer Sain Dixit', initials: 'VSD', maxHours: 16, department: 'Computer Science' },
  { id: 'UOA', name: 'Ms. Uma Ojha', initials: 'UOA', maxHours: 16, department: 'Computer Science' },
  { id: 'JMN', name: 'Mr. Jag Mohan', initials: 'JMN', maxHours: 16, department: 'Computer Science' },
  { id: 'PJN', name: 'Dr. Parul Jain', initials: 'PJN', maxHours: 16, department: 'Computer Science' },
  { id: 'DSH', name: 'Mr. Dharmendra Singh', initials: 'DSH', maxHours: 16, department: 'Computer Science' },
  { id: 'MYV', name: 'Mr. Manvendra Yadav', initials: 'MYV', maxHours: 16, department: 'Computer Science' },
  { id: 'MCN', name: 'Ms. Manisha Chouhan', initials: 'MCN', maxHours: 16, department: 'Computer Science' },
  { id: 'LKS', name: 'Dr. Lokesh Kumar Srivastava', initials: 'LKS', maxHours: 16, department: 'Computer Science' },
  { id: 'MKR', name: 'Mr. Mahesh Kumar', initials: 'MKR', maxHours: 16, department: 'Computer Science' },
  { id: 'RKR', name: 'Dr. Roushan Kumar', initials: 'RKR', maxHours: 16, department: 'Computer Science' },
];

// Full subject data from PDF
const INITIAL_SUBJECTS = [
  // CS(H) subjects
  { id: 's1', course: 'CS(H)', semester: 1, name: 'Mathematics for Computing', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 55, department: 'Computer Science' },
  { id: 's2', course: 'CS(H)', semester: 1, name: 'OOPS using python', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 55, department: 'Computer Science' },
  { id: 's3', course: 'CS(H)', semester: 1, name: 'Computer System Architecture', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 55, department: 'Computer Science' },
  { id: 's4', course: 'CS(H)', semester: 3, name: 'Data Structures', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's5', course: 'CS(H)', semester: 3, name: 'Artificial Intelligence', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's6', course: 'CS(H)', semester: 3, name: 'Operating System', section: '', type: 'DSC', le: 3, tu: 0, pr: 1, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's7', course: 'CS(H)', semester: 3, name: 'Data Mining', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 51, department: 'Computer Science' },
  { id: 's8', course: 'CS(H)', semester: 5, name: 'Algo and Adv Data Structures', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 47, department: 'Computer Science' },
  { id: 's9', course: 'CS(H)', semester: 5, name: 'Theory of Computation', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 47, department: 'Computer Science' },
  { id: 's10', course: 'CS(H)', semester: 5, name: 'Software Engineering', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 47, department: 'Computer Science' },
  { id: 's11', course: 'CS(H)', semester: 5, name: 'Data Privacy', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 47, department: 'Computer Science' },
  { id: 's12', course: 'CS(H)', semester: 7, name: 'Compiler Design', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 43, department: 'Computer Science' },
  { id: 's13', course: 'CS(H)', semester: 7, name: 'Digital Image Processing', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 43, department: 'Computer Science' },
  { id: 's14', course: 'CS(H)', semester: 7, name: 'Advanced Algorithm', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 43, department: 'Computer Science' },
  { id: 's15', course: 'CS(H)+CA(P)', semester: 7, name: 'Cyber Forensics', section: '', type: 'DSE', le: 3, tu: 0, pr: 1, hasLab: true, students: 81, department: 'Computer Science', isMerged: true },
  
  // CS(P) subjects
  { id: 's16', course: 'CS(P)', semester: 1, name: 'Programming using C++', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 50, department: 'Computer Science' },
  { id: 's17', course: 'CS(P)', semester: 3, name: 'OOPS using Python', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 46, department: 'Computer Science' },
  { id: 's18', course: 'CS(P)', semester: 3, name: 'Design and Analysis of Algo', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 46, department: 'Computer Science' },
  { id: 's19', course: 'CS(P)', semester: 5, name: 'Database Management System', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 42, department: 'Computer Science' },
  { id: 's20', course: 'CS(P)', semester: 5, name: 'Data Mining', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 42, department: 'Computer Science' },
  { id: 's21', course: 'CS(P)+CA(P)', semester: 7, name: 'Design and Analysis of Algo', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 76, department: 'Computer Science', isMerged: true },
  { id: 's22', course: 'CS(P)+CA(P)', semester: 7, name: 'Digital Image Processing', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 76, department: 'Computer Science', isMerged: true },
  { id: 's23', course: 'CS(P)', semester: 7, name: 'Machine Learning', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 38, department: 'Computer Science' },
  { id: 's24', course: 'CS(P)+CA(P)', semester: 7, name: 'Research Methodology', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 76, department: 'Computer Science', isMerged: true },
  
  // CA(P) subjects
  { id: 's25', course: 'CA(P)', semester: 1, name: 'Programming using C++', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 50, department: 'Computer Science' },
  { id: 's26', course: 'CA(P)', semester: 1, name: 'OOPS using Python', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 50, department: 'Computer Science' },
  { id: 's27', course: 'CA(P)', semester: 3, name: 'Design and Analysis of Algo', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 46, department: 'Computer Science' },
  { id: 's28', course: 'CA(P)', semester: 3, name: 'Data Mining', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 46, department: 'Computer Science' },
  { id: 's29', course: 'CA(P)', semester: 5, name: 'Database Management System', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 42, department: 'Computer Science' },
  { id: 's30', course: 'CA(P)', semester: 5, name: 'Web Design and Development', section: '', type: 'DSC', le: 3, tu: 0, pr: 2, hasLab: true, students: 42, department: 'Computer Science' },
  { id: 's31', course: 'CA(P)', semester: 5, name: 'Machine Learning', section: '', type: 'DSE', le: 3, tu: 0, pr: 2, hasLab: true, students: 42, department: 'Computer Science' },
  
  // GE subjects
  { id: 's32', course: 'COMMON', semester: 1, name: 'Programming using C++', section: 'A', type: 'GE', le: 3, tu: 0, pr: 2, hasLab: true, students: 30, department: 'Computer Science' },
  { id: 's33', course: 'COMMON', semester: 1, name: 'Programming using C++', section: 'B', type: 'GE', le: 3, tu: 0, pr: 2, hasLab: true, students: 30, department: 'Computer Science' },
  { id: 's34', course: 'COMMON', semester: 3, name: 'Database Management System', section: 'A', type: 'GE', le: 3, tu: 0, pr: 2, hasLab: true, students: 30, department: 'Computer Science' },
  { id: 's35', course: 'COMMON', semester: 3, name: 'Database Management System', section: 'B', type: 'GE', le: 3, tu: 0, pr: 2, hasLab: true, students: 30, department: 'Computer Science' },
  { id: 's36', course: 'COMMON', semester: 5, name: 'Operating System', section: '', type: 'GE', le: 3, tu: 0, pr: 2, hasLab: true, students: 50, department: 'Computer Science' },
  { id: 's37', course: 'COMMON', semester: 7, name: 'Design and Analysis of Algo', section: '', type: 'GE', le: 3, tu: 0, pr: 2, hasLab: true, students: 48, department: 'Computer Science' },
  
  // SEC subjects
  { id: 's38', course: 'COMMON', semester: 1, name: 'IT Skills and Data Analysis 1', section: '', type: 'SEC', le: 0, tu: 0, pr: 4, hasLab: true, students: 70, department: 'Computer Science' },
  { id: 's39', course: 'COMMON', semester: 3, name: 'IT Skills and Data Analysis 1', section: '', type: 'SEC', le: 0, tu: 0, pr: 4, hasLab: true, students: 70, department: 'Computer Science' },
  { id: 's40', course: 'COMMON', semester: 5, name: 'Latex Type setting for Beginners', section: '', type: 'SEC', le: 0, tu: 0, pr: 3, hasLab: true, students: 60, department: 'Computer Science' },
  
  // VAC subjects
  { id: 's41', course: 'COMMON', semester: 1, name: 'Digital Empowerment', section: '', type: 'VAC', le: 0, tu: 0, pr: 4, hasLab: true, students: 50, department: 'Computer Science' },
];

const TimetablePlanner = () => {
  const [subjects, setSubjects] = useState(INITIAL_SUBJECTS);
  const [assignments, setAssignments] = useState({});
  const [lockedAssignments, setLockedAssignments] = useState(new Set());
  const [teacherPreferences, setTeacherPreferences] = useState({});
  const [draggedTeacher, setDraggedTeacher] = useState(null);
  const [searchTeacher, setSearchTeacher] = useState('');
  const [searchSubject, setSearchSubject] = useState('');
  const [filterSemester, setFilterSemester] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [labRatio, setLabRatio] = useState(20);
  const [showLabAssistant, setShowLabAssistant] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [selectedTeacherForPref, setSelectedTeacherForPref] = useState(null);
  const [showValidationDetails, setShowValidationDetails] = useState(false);
  const [showUnassignedOnly, setShowUnassignedOnly] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('timetable-assignments');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        setAssignments(data.assignments || {});
        setLockedAssignments(new Set(data.locked || []));
        setTeacherPreferences(data.preferences || {});
      } catch (e) {
        console.error('Failed to load saved data');
      }
    }
  }, []);

  // Save to localStorage
  const saveToStorage = () => {
    const data = {
      assignments,
      locked: Array.from(lockedAssignments),
      preferences: teacherPreferences
    };
    localStorage.setItem('timetable-assignments', JSON.stringify(data));
    alert('✅ Saved successfully!');
  };

  // Calculate teacher workload
  const getTeacherWorkload = (teacherId) => {
    let totalHours = 0;
    let subjectCount = 0;
    const subjectDetails = [];
    
    Object.entries(assignments).forEach(([subjectId, data]) => {
      const subject = subjects.find(s => s.id === subjectId);
      if (!subject) return;

      if (data.mainTeacher === teacherId) {
        const hours = data.assignedLe + data.assignedTu + data.assignedPr;
        totalHours += hours;
        subjectCount++;
        subjectDetails.push({ subject: subject.name, hours, role: 'Main' });
      }
      if (data.coTeachers?.includes(teacherId)) {
        const hours = data.assignedLe + data.assignedTu + data.assignedPr;
        totalHours += hours;
        subjectCount++;
        subjectDetails.push({ subject: subject.name, hours, role: 'Co-teacher' });
      }
      if (data.assistants?.includes(teacherId)) {
        // Lab assistants count for partial hours
        const hours = data.assignedPr / 2;
        totalHours += hours;
        subjectDetails.push({ subject: subject.name, hours, role: 'Lab Assistant' });
      }
    });
    
    return { totalHours, subjectCount, subjectDetails };
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

  // Calculate lab assistants needed
  const getLabAssistantsNeeded = (subject) => {
    if (!subject.hasLab || subject.pr === 0) return 0;
    return Math.ceil(subject.students / labRatio);
  };

  // Get available teachers for lab assistant
  const getAvailableLabAssistants = (subjectId) => {
    const subject = subjects.find(s => s.id === subjectId);
    if (!subject) return [];

    return TEACHERS.filter(teacher => {
      const { totalHours } = getTeacherWorkload(teacher.id);
      const assignment = assignments[subjectId];
      
      // Don't suggest if already main teacher or co-teacher
      if (assignment?.mainTeacher === teacher.id) return false;
      if (assignment?.coTeachers?.includes(teacher.id)) return false;
      if (assignment?.assistants?.includes(teacher.id)) return false;
      
      // Has capacity for at least 1 hour
      return totalHours < teacher.maxHours - 1;
    }).sort((a, b) => {
      const aLoad = getTeacherWorkload(a.id).totalHours;
      const bLoad = getTeacherWorkload(b.id).totalHours;
      return aLoad - bLoad; // Sort by least loaded first
    });
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

    const existingAssignment = assignments[subjectId];
    
    if (!existingAssignment) {
      // New assignment
      setAssignments(prev => ({
        ...prev,
        [subjectId]: {
          mainTeacher: draggedTeacher.id,
          coTeachers: [],
          assistants: [],
          assignedLe: subject.le,
          assignedTu: subject.tu,
          assignedPr: subject.pr,
        }
      }));
    } else {
      // Add as co-teacher
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

  // Add lab assistant
  const addLabAssistant = (subjectId, teacherId) => {
    const assignment = assignments[subjectId];
    if (!assignment) return;

    if (!assignment.assistants.includes(teacherId)) {
      setAssignments(prev => ({
        ...prev,
        [subjectId]: {
          ...prev[subjectId],
          assistants: [...(prev[subjectId].assistants || []), teacherId]
        }
      }));
    }
  };

  // Remove teacher
  const removeTeacher = (subjectId, teacherId, role = 'main') => {
    if (lockedAssignments.has(subjectId)) {
      if (!window.confirm('This assignment is locked. Remove anyway?')) return;
    }

    if (role === 'main') {
      const newAssignments = { ...assignments };
      delete newAssignments[subjectId];
      setAssignments(newAssignments);
      lockedAssignments.delete(subjectId);
      setLockedAssignments(new Set(lockedAssignments));
    } else if (role === 'co') {
      setAssignments(prev => ({
        ...prev,
        [subjectId]: {
          ...prev[subjectId],
          coTeachers: prev[subjectId].coTeachers.filter(id => id !== teacherId)
        }
      }));
    } else if (role === 'assistant') {
      setAssignments(prev => ({
        ...prev,
        [subjectId]: {
          ...prev[subjectId],
          assistants: prev[subjectId].assistants.filter(id => id !== teacherId)
        }
      }));
    }
  };

  // Toggle lock
  const toggleLock = (subjectId) => {
    const newLocked = new Set(lockedAssignments);
    if (newLocked.has(subjectId)) {
      newLocked.delete(subjectId);
    } else {
      newLocked.add(subjectId);
    }
    setLockedAssignments(newLocked);
  };

  // Reset unlocked assignments
  const resetUnlocked = () => {
    if (!window.confirm('Reset all unlocked assignments?')) return;
    
    const newAssignments = {};
    Object.keys(assignments).forEach(subjectId => {
      if (lockedAssignments.has(subjectId)) {
        newAssignments[subjectId] = assignments[subjectId];
      }
    });
    setAssignments(newAssignments);
  };

  // Teacher preferences
  const toggleDayOff = (teacherId, day) => {
    setTeacherPreferences(prev => {
      const current = prev[teacherId] || { offDays: [] };
      const offDays = current.offDays.includes(day)
        ? current.offDays.filter(d => d !== day)
        : [...current.offDays, day];
      return { ...prev, [teacherId]: { ...current, offDays } };
    });
  };

  // Export to CSV
  const exportToCSV = () => {
    const rows = [];
    const header = 'Course,Semester,Subject,Section,Teacher,Hours Taught(Le,Tu,Pr),Department,Subject_type,Has_Lab,Notes\n';
    
    subjects.forEach(subject => {
      const assignment = assignments[subject.id];
      if (!assignment) return;

      const teacher = TEACHERS.find(t => t.id === assignment.mainTeacher);
      const coTeachers = assignment.coTeachers.map(id => TEACHERS.find(t => t.id === id)?.name).filter(Boolean);
      
      let teacherStr = teacher.name;
      if (coTeachers.length > 0) {
        teacherStr += ', ' + coTeachers.join(', ');
      }

      const notes = assignment.assistants?.length > 0 
        ? `Lab Assistants: ${assignment.assistants.map(id => TEACHERS.find(t => t.id === id)?.initials).join(', ')}`
        : '';

      rows.push([
        subject.course,
        subject.semester,
        subject.name,
        subject.section,
        teacherStr,
        `${assignment.assignedLe},${assignment.assignedTu},${assignment.assignedPr}`,
        subject.department,
        subject.type,
        subject.hasLab ? 'yes' : 'no',
        notes
      ].join(','));
    });

    const csv = header + rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'timetable_input.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Validation
  const getValidationStats = () => {
    const errors = [];
    const warnings = [];
    const success = [];

    TEACHERS.forEach(teacher => {
      const { totalHours } = getTeacherWorkload(teacher.id);
      if (totalHours > teacher.maxHours) {
        errors.push(`${teacher.name} overloaded: ${totalHours.toFixed(1)}h/${teacher.maxHours}h`);
      } else if (totalHours >= teacher.maxHours * 0.8) {
        success.push(`${teacher.name}: ${totalHours.toFixed(1)}h/${teacher.maxHours}h (optimal)`);
      } else if (totalHours < teacher.maxHours * 0.5 && totalHours > 0) {
        warnings.push(`${teacher.name} underutilized: ${totalHours.toFixed(1)}h/${teacher.maxHours}h`);
      }
    });

    subjects.forEach(subject => {
      const status = getSubjectStatus(subject);
      const assignment = assignments[subject.id];
      
      if (!assignment) {
        errors.push(`${subject.name} (${subject.course} Sem${subject.semester}): No teacher assigned`);
      } else if (status.hours < status.total) {
        warnings.push(`${subject.name}: ${status.hours}h/${status.total}h assigned`);
      }

      // Lab assistant check
      if (subject.hasLab && subject.pr > 0 && assignment) {
        const needed = getLabAssistantsNeeded(subject);
        const assigned = assignment.assistants?.length || 0;
        if (assigned < needed) {
          warnings.push(`${subject.name}: Needs ${needed} lab assistants, has ${assigned}`);
        }
      }
    });

    return { errors, warnings, success };
  };

  const validation = getValidationStats();

  // Filters
  const filteredTeachers = TEACHERS.filter(t => 
    t.name.toLowerCase().includes(searchTeacher.toLowerCase()) ||
    t.initials.toLowerCase().includes(searchTeacher.toLowerCase())
  );

  const filteredSubjects = subjects.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(searchSubject.toLowerCase()) ||
                          s.course.toLowerCase().includes(searchSubject.toLowerCase());
    const matchesSemester = filterSemester === 'all' || s.semester === parseInt(filterSemester);
    const matchesType = filterType === 'all' || s.type === filterType;
    const matchesUnassigned = !showUnassignedOnly || !assignments[s.id];
    return matchesSearch && matchesSemester && matchesType && matchesUnassigned;
  });

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Timetable Planner</h1>
            <div className="flex gap-2">
              <button
                onClick={saveToStorage}
                className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
              >
                <Save size={16} />
                Save
              </button>
              <button
                onClick={resetUnlocked}
                className="flex items-center gap-2 px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm"
              >
                <RotateCcw size={16} />
                Reset Unlocked
              </button>
              <button
                onClick={exportToCSV}
                className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                <Download size={16} />
                Export CSV
              </button>
            </div>
          </div>

          {/* Validation Status */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="flex items-center gap-2 p-2 bg-red-50 rounded-lg cursor-pointer" onClick={() => setShowValidationDetails(!showValidationDetails)}>
              <AlertCircle className="text-red-600" size={18} />
              <div>
                <div className="text-xl font-bold text-red-600">{validation.errors.length}</div>
                <div className="text-xs text-red-700">Errors</div>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 bg-yellow-50 rounded-lg cursor-pointer" onClick={() => setShowValidationDetails(!showValidationDetails)}>
              <AlertTriangle className="text-yellow-600" size={18} />
              <div>
                <div className="text-xl font-bold text-yellow-600">{validation.warnings.length}</div>
                <div className="text-xs text-yellow-700">Warnings</div>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg cursor-pointer" onClick={() => setShowValidationDetails(!showValidationDetails)}>
              <CheckCircle className="text-green-600" size={18} />
              <div>
                <div className="text-xl font-bold text-green-600">{validation.success.length}</div>
                <div className="text-xs text-green-700">OK</div>
              </div>
            </div>
          </div>

          {/* Lab Assistant Panel Toggle */}
          <button
            onClick={() => setShowLabAssistant(!showLabAssistant)}
            className="w-full flex items-center justify-between p-3 bg-purple-50 rounded-lg hover:bg-purple-100 text-sm"
          >
            <span className="font-semibold text-purple-900">
              🧪 Lab Assistant Calculator
            </span>
            {showLabAssistant ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      </div>

      {/* Lab Assistant Panel */}
      {showLabAssistant && (
        <div className="max-w-7xl mx-auto mb-4 bg-white rounded-lg shadow p-4">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-sm font-semibold">Student:Teacher Ratio:</span>
            <input
              type="range"
              min="15"
              max="30"
              value={labRatio}
              onChange={(e) => setLabRatio(parseInt(e.target.value))}
              className="flex-1"
            />
            <span className="text-lg font-bold text-purple-600">1:{labRatio}</span>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto">
            {subjects
              .filter(s => s.hasLab && s.pr > 0)
              .sort((a, b) => b.students - a.students)
              .map(subject => {
                const needed = getLabAssistantsNeeded(subject);
                const assignment = assignments[subject.id];
                const assigned = assignment?.assistants?.length || 0;
                const available = getAvailableLabAssistants(subject.id);

                return (
                  <div key={subject.id} className={`p-3 rounded-lg border-2 ${assigned >= needed ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-semibold text-sm">{subject.name}</div>
                        <div className="text-xs text-gray-600">
                          {subject.course} Sem{subject.semester} • 👥 {subject.students} students
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${assigned >= needed ? 'text-green-600' : 'text-red-600'}`}>
                          {assigned}/{needed}
                        </div>
                        <div className="text-xs text-gray-600">assistants</div>
                      </div>
                    </div>

                    {assigned < needed && available.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        <span className="text-xs text-gray-600">Suggest:</span>
                        {available.slice(0, needed - assigned).map(teacher => (
                          <button
                            key={teacher.id}
                            onClick={() => addLabAssistant(subject.id, teacher.id)}
                            className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                          >
                            + {teacher.initials}
                          </button>
                        ))}
                      </div>
                    )}

                    {assignment?.assistants && assignment.assistants.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {assignment.assistants.map(teacherId => {
                          const teacher = TEACHERS.find(t => t.id === teacherId);
                          return (
                            <div key={teacherId} className="flex items-center gap-1 px-2 py-1 bg-purple-100 rounded text-xs">
                              <span>{teacher?.initials}</span>
                              <button
                                onClick={() => removeTeacher(subject.id, teacherId, 'assistant')}
                                className="text-red-600 hover:text-red-800"
                              >
                                <X size={12} />
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto grid grid-cols-2 gap-4">
        {/* Teachers Panel */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold">Teachers</h2>
            <button
              onClick={() => setShowPreferences(true)}
              className="text-sm flex items-center gap-1 px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
            >
              <Calendar size={14} />
              Preferences
            </button>
          </div>
          
          <input
            type="text"
            placeholder="Search teachers..."
            value={searchTeacher}
            onChange={(e) => setSearchTeacher(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg mb-3 text-sm"
          />
          
          <div className="space-y-2 max-h-[70vh] overflow-y-auto">
            {filteredTeachers.map(teacher => {
              const { totalHours, subjectCount, subjectDetails } = getTeacherWorkload(teacher.id);
              const colorClass = getWorkloadColor(totalHours, teacher.maxHours);
              const prefs = teacherPreferences[teacher.id];
              
              return (
                <div
                  key={teacher.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, teacher)}
                  className={`p-3 border-2 rounded-lg cursor-move transition-all hover:shadow-md animate-slide-in ${colorClass}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-sm">{teacher.name}</div>
                      <div className="text-xs mt-1">
                        {totalHours.toFixed(1)}h / {teacher.maxHours}h • {subjectCount} subjects
                      </div>
                      <div className="text-xs opacity-75">{teacher.initials}</div>
                      {prefs?.offDays && prefs.offDays.length > 0 && (
                        <div className="text-xs mt-1 text-blue-600">
                          🏖️ Off: {prefs.offDays.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {subjectDetails.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      {subjectDetails.map((detail, idx) => (
                        <div key={idx} className="text-xs text-gray-700">
                          • {detail.subject} ({detail.hours.toFixed(1)}h) {detail.role !== 'Main' && `[${detail.role}]`}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Subjects Panel */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-bold mb-3">Subjects</h2>
          
          <div className="space-y-2 mb-3">
            <input
              type="text"
              placeholder="Search subjects..."
              value={searchSubject}
              onChange={(e) => setSearchSubject(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
            
            <div className="flex gap-2">
              <select
                value={filterSemester}
                onChange={(e) => setFilterSemester(e.target.value)}
                className="flex-1 px-3 py-2 border rounded-lg text-sm"
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
                className="flex-1 px-3 py-2 border rounded-lg text-sm"
              >
                <option value="all">All Types</option>
                <option value="DSC">DSC</option>
                <option value="DSE">DSE</option>
                <option value="GE">GE</option>
                <option value="SEC">SEC</option>
                <option value="VAC">VAC</option>
              </select>
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={showUnassignedOnly}
                onChange={(e) => setShowUnassignedOnly(e.target.checked)}
                className="rounded"
              />
              Show unassigned only
            </label>
          </div>

          <div className="space-y-2 max-h-[70vh] overflow-y-auto">
            {filteredSubjects.map(subject => {
              const assignment = assignments[subject.id];
              const status = getSubjectStatus(subject);
              const isComplete = status.complete;
              const isLocked = lockedAssignments.has(subject.id);
              
              return (
                <div
                  key={subject.id}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => handleDrop(e, subject.id)}
                  className={`p-3 border-2 rounded-lg transition-all animate-slide-in ${
                    isComplete 
                      ? 'border-green-400 bg-green-50' 
                      : assignment 
                        ? 'border-yellow-400 bg-yellow-50'
                        : 'border-gray-300 bg-white hover:border-blue-400 hover:shadow-md'
                  } ${isLocked ? 'ring-2 ring-blue-400' : ''}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-semibold text-sm flex items-center gap-2">
                        {subject.name}
                        {subject.isMerged && <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">MERGED</span>}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        {subject.course} {subject.section && `Sec ${subject.section}`} • Sem{subject.semester} • {subject.type}
                      </div>
                      <div className="text-xs mt-1">
                        {subject.le}L + {subject.tu}T + {subject.pr}P ({status.hours}/{status.total}h)
                      </div>
                      <div className="text-xs text-gray-600">👥 {subject.students} students</div>
                    </div>
                    
                    {assignment && (
                      <button
                        onClick={() => toggleLock(subject.id)}
                        className={`p-1 rounded ${isLocked ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                      >
                        {isLocked ? <Lock size={16} /> : <Unlock size={16} />}
                      </button>
                    )}
                  </div>
                  
                  {assignment && (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between p-2 bg-white rounded border text-xs">
                        <span className="font-medium">
                          {TEACHERS.find(t => t.id === assignment.mainTeacher)?.name}
                        </span>
                        <button
                          onClick={() => removeTeacher(subject.id, assignment.mainTeacher)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <X size={14} />
                        </button>
                      </div>
                      
                      {assignment.coTeachers?.map(coTeacherId => (
                        <div key={coTeacherId} className="flex items-center justify-between p-2 bg-blue-50 rounded border border-blue-200 text-xs">
                          <span>
                            {TEACHERS.find(t => t.id === coTeacherId)?.name} <span className="text-blue-600">(Co)</span>
                          </span>
                          <button
                            onClick={() => removeTeacher(subject.id, coTeacherId, 'co')}
                            className="text-red-600 hover:text-red-800"
                          >
                            <X size={14} />
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

      {/* Validation Details Modal */}
      {showValidationDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 modal-backdrop">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6 modal-content">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Validation Details</h3>
              <button onClick={() => setShowValidationDetails(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            {validation.errors.length > 0 && (
              <div className="mb-4">
                <div className="font-semibold text-red-600 mb-2 flex items-center gap-2">
                  <AlertCircle size={18} />
                  Errors ({validation.errors.length})
                </div>
                <ul className="space-y-1 ml-6">
                  {validation.errors.map((error, i) => (
                    <li key={i} className="text-sm text-red-700">• {error}</li>
                  ))}
                </ul>
              </div>
            )}

            {validation.warnings.length > 0 && (
              <div className="mb-4">
                <div className="font-semibold text-yellow-600 mb-2 flex items-center gap-2">
                  <AlertTriangle size={18} />
                  Warnings ({validation.warnings.length})
                </div>
                <ul className="space-y-1 ml-6">
                  {validation.warnings.map((warning, i) => (
                    <li key={i} className="text-sm text-yellow-700">• {warning}</li>
                  ))}
                </ul>
              </div>
            )}

            {validation.success.length > 0 && (
              <div>
                <div className="font-semibold text-green-600 mb-2 flex items-center gap-2">
                  <CheckCircle size={18} />
                  Success ({validation.success.length})
                </div>
                <ul className="space-y-1 ml-6">
                  {validation.success.slice(0, 10).map((success, i) => (
                    <li key={i} className="text-sm text-green-700">• {success}</li>
                  ))}
                  {validation.success.length > 10 && (
                    <li className="text-sm text-green-600 italic">... and {validation.success.length - 10} more</li>
                  )}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Teacher Preferences Modal */}
      {showPreferences && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 modal-backdrop">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto p-6 modal-content">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Teacher Preferences</h3>
              <button onClick={() => setShowPreferences(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              {TEACHERS.map(teacher => {
                const prefs = teacherPreferences[teacher.id] || { offDays: [] };
                const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

                return (
                  <div key={teacher.id} className="p-4 border rounded-lg">
                    <div className="font-semibold mb-2">{teacher.name}</div>
                    <div className="flex gap-2">
                      {days.map(day => (
                        <button
                          key={day}
                          onClick={() => toggleDayOff(teacher.id, day)}
                          className={`px-3 py-1 rounded text-sm ${
                            prefs.offDays.includes(day)
                              ? 'bg-red-500 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {day}
                        </button>
                      ))}
                    </div>
                    {prefs.offDays.length > 0 && (
                      <div className="text-xs text-gray-600 mt-2">
                        Off days: {prefs.offDays.join(', ')}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimetablePlanner;