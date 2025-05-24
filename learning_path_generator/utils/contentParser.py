import re

def parse_learning_path_content(content):
    tasks = []
    order = 0

    # Parse prerequisites
    prerequisites_match = re.search(r'Prerequisites\s*(.*?)(?=Week \d+:|Path:|Month \d+:)', content, re.DOTALL)
    if prerequisites_match:
        prereq_content = prerequisites_match.group(1).strip()
        tasks.append({
            'title': 'Prerequisites',
            'description': prereq_content,
            'category': 'PREREQUISITE',
            'order': order
        })
        order += 1

    # Find all month/week sections
    # First, try to match month sections
    month_pattern = r'Month (\d+):.*?(?=Month \d+:|Additional Resources|$)'
    month_sections = list(re.finditer(month_pattern, content, re.DOTALL))
    
    if month_sections:  # If months are found
        for month_section in month_sections:
            month_content = month_section.group(0)
            month_num = int(re.search(r'Month (\d+):', month_content).group(1))
            
            # Find weeks within month
            week_pattern = r'Week (\d+):(.*?)(?=Week \d+:|$)'
            weeks = re.finditer(week_pattern, month_content, re.DOTALL)
            
            for week_match in weeks:
                week_num = int(week_match.group(1))
                week_content = week_match.group(2).strip()
                
                # Parse days within week
                day_pattern = r'Days? (\d+-\d+):(.*?)(?=Days? \d+-\d+:|Week \d+:|$)'
                days = re.finditer(day_pattern, week_content, re.DOTALL)
                
                for day_match in days:
                    day_range = day_match.group(1)
                    task_content = day_match.group(2).strip()
                    
                    tasks.append({
                        'title': f'Month {month_num} - Week {week_num} - Days {day_range}',
                        'description': task_content,
                        'category': 'WEEK',
                        'week_number': week_num,
                        'day_range': day_range,
                        'order': order
                    })
                    order += 1
    else:  # If no months found, try weeks directly
        week_pattern = r'Week (\d+):(.*?)(?=Week \d+:|Additional Resources|$)'
        weeks = re.finditer(week_pattern, content, re.DOTALL)
        
        for week_match in weeks:
            week_num = int(week_match.group(1))
            week_content = week_match.group(2)
            
            # Parse days within week
            day_pattern = r'Days? (\d+-\d+):(.*?)(?=Days? \d+-\d+:|Week \d+:|$)'
            days = re.finditer(day_pattern, week_content, re.DOTALL)
            
            for day_match in days:
                day_range = day_match.group(1)
                task_content = day_match.group(2).strip()
                
                tasks.append({
                    'title': f'Week {week_num} - Days {day_range}',
                    'description': task_content,
                    'category': 'WEEK',
                    'week_number': week_num,
                    'day_range': day_range,
                    'order': order
                })
                order += 1

    # Parse additional resources
    resources_match = re.search(r'Additional Resources:?(.*?)(?=Progress Tracking:|$)', content, re.DOTALL)
    if resources_match:
        resource_content = resources_match.group(1).strip()
        tasks.append({
            'title': 'Additional Resources',
            'description': resource_content,
            'category': 'RESOURCE',
            'order': order
        })
        order += 1

    return tasks