import { Component } from '@angular/core';
import { TaskService } from '../../services/task.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-tasks',
  imports: [FormsModule, CommonModule],
  templateUrl: './tasks.component.html',
  styleUrl: './tasks.component.scss'
})
export class TasksComponent {

  file_id: string = '';
  pipeline_id: string= '';
  status_message: string = '';
  is_processing:boolean = false;
  output_message: string = '';
  

  constructor(private taskService: TaskService) { }

  ngOnInit() {
  }

  submitTask() {
    if (!this.file_id || !this.pipeline_id) {
      this.status_message = 'Please enter both File ID and Pipeline ID.';
      return;
    }

    this.is_processing = true;
    this.status_message = 'Submitting task...';
    
     this.taskService.submitTask(this.file_id, this.pipeline_id).subscribe(
      response => {
        this.pollTaskStatus(response.id);
      },
      error => {
        this.is_processing = false;
        this.status_message = 'Error submitting task.';
      }
    ); 
  }

  pollTaskStatus(taskId: string) {
    this.taskService.pollTaskStatus(taskId).subscribe(
      (response: any) => {
        if (response.state === 'COMPLETE') {
          this.output_message = response.logs?.[0]?.logs?.[0]?.stdout || 'No output found.';
          this.status_message = 'Task completed!';
          console.log(response)
          this.is_processing = false;
        } else if (response.state === 'SYSTEM_ERROR' || response.state === 'EXECUTOR_ERROR') {
          this.status_message = 'Task failed.';
          this.is_processing = false;
        }
      },
      error => {
        this.is_processing = false;
        this.status_message = 'Error fetching task status.';
      }
    );
  }



}
