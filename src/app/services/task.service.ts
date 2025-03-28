import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { interval, Observable, switchMap, takeWhile } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  private backendUrl = 'http://localhost:8080';

  constructor(private http:HttpClient) { }

  submitTask(fileId: string, pipelineId: string): Observable<any> {
    return this.http.post(`${this.backendUrl}/run-task`, { file_id: fileId, pipeline_id: pipelineId }, { withCredentials: true });
  }

  pollTaskStatus(taskId: string): Observable<any> {
    return interval(8080).pipe(
      switchMap(() => this.http.get(`${this.backendUrl}/run-task/${taskId}`)),
      takeWhile((response: any) => response.state !== 'COMPLETE' && response.state !== 'SYSTEM_ERROR' &&  response.state !== 'EXECUTOR_ERROR', true) // Stop when done
    );
  }
}
