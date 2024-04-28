package com.rtbhouse;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class WorkerServlet extends HttpServlet {
    public WorkerServlet() {
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        RequestProcessor processor = new RequestProcessor();
        processor.process(request, response);
    }
}
