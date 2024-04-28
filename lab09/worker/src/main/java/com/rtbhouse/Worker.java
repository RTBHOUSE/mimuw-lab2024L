package com.rtbhouse;

import org.eclipse.jetty.server.Connector;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.ServerConnector;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.util.BlockingArrayQueue;
import org.eclipse.jetty.util.thread.QueuedThreadPool;
import org.eclipse.jetty.util.thread.ThreadPool;

public class Worker {
    private static final int JETTY_PORT = 8000;
    private static final int JETTY_MIN_THREADS = 32;
    private static final int JETTY_MAX_THREADS = 32;
    private static final int JETTY_QUEUE_CAPACITY = 16384;

    public static void main(String[] args) throws Exception {
        Worker worker = new Worker();
        worker.run();
    }

    public void run() throws Exception {
        Server server = new Server(buildThreadPool());
        server.setConnectors(buildConnectors(server));
        server.setHandler(buildServletContextHandler());
        server.start();

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try {
                server.stop();
            } catch (Exception e) {
                System.out.println(e);
            }
        }));
    }

    private ThreadPool buildThreadPool() {
        return new QueuedThreadPool(JETTY_MAX_THREADS, JETTY_MIN_THREADS, new BlockingArrayQueue<>(JETTY_QUEUE_CAPACITY));
    }

    private Connector[] buildConnectors(Server server) {
        ServerConnector connector = new ServerConnector(server);
        connector.setPort(JETTY_PORT);

        return new Connector[] { connector };
    }
    private ServletContextHandler buildServletContextHandler() {
        ServletContextHandler servletHandler = new ServletContextHandler();
        servletHandler.addServlet(WorkerServlet.class, "/");
        return servletHandler;
    }
}
