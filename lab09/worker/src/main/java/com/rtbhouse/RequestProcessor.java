package com.rtbhouse;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import javax.servlet.AsyncContext;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class RequestProcessor {
    private static final ThreadPoolExecutor REQUEST_PROCESSING_EXECUTOR = new ThreadPoolExecutor(2, 2, 60000L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<>(16384));

    private AsyncContext asyncContext;

    public RequestProcessor() {
    }

    public void process(HttpServletRequest request, HttpServletResponse response) {
        AsyncContext asyncContext = request.startAsync(request, response);

        REQUEST_PROCESSING_EXECUTOR.submit(() -> this.processAsync(asyncContext));
    }

    private void processAsync(AsyncContext asyncContext) {
        HttpServletRequest request = (HttpServletRequest) asyncContext.getRequest();
        HttpServletResponse response = (HttpServletResponse) asyncContext.getResponse();

        int n = Integer.parseInt(request.getParameter("n"));
        double result = doWork(n);

        try {
            PrintWriter responseWriter = response.getWriter();
            responseWriter.println(result);
            responseWriter.flush();
        } catch (IOException e) {
            System.out.println(e);
        }

        asyncContext.complete();
    }

    private double doWork(int n) {
        double result = Math.sqrt(ThreadLocalRandom.current().nextDouble());

        for (int i = 0; i < n; i++) {
            double rand = ThreadLocalRandom.current().nextDouble();
            result = (result + Math.sqrt(rand)) / 2;
        }

        return result;
    }
}
